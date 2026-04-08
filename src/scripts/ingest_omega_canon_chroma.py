#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 (MIGRATIONPLAN_OMEGA_WISSEN_DBS): Kanon-Dokumente → ChromaDB `core_canon`.

- Quelle: PostgreSQL `omega_canon_documents` (list_canon_documents) oder --from-disk (Anker + Seeds, wie Sync).
- Collection: COLLECTION_CORE_CANON (Default: core_canon), Embedding DefaultEmbeddingFunction (384 dim) + Gitter-Snap.
- Metadaten: Zero-State-kompatibel — type=context, source_collection=core_canon, source_file=repo_path, chunk_index, …

Usage:
  cd /OMEGA_CORE && PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.scripts.ingest_omega_canon_chroma
  PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.scripts.ingest_omega_canon_chroma --from-disk --dry-run

Nach PG-Sync automatisch (optional): OMEGA_CANON_CHROMA_AFTER_SYNC=1
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=True)

def _is_text_canon_path(repo_path: str) -> bool:
    low = repo_path.lower()
    if low.endswith(".yml"):
        return True
    for suf in (".md", ".mdc", ".py", ".sql", ".yaml", ".json", ".ts", ".tsx", ".toml", ".txt"):
        if low.endswith(suf):
            return True
    return False


def chunk_canon_text(text: str, max_chars: int, overlap: int) -> list[str]:
    """
    Zerlegt Fließtext in überlappende Chunks (A6: Grenzen sind int — hier nur Längen).
    Leerstring → keine Chunks.
    """
    if max_chars < 200:
        max_chars = 200
    if overlap < 0 or overlap >= max_chars:
        overlap = min(80, max_chars // 8)
    stripped = text.strip()
    if not stripped:
        return []
    paras = [p.strip() for p in stripped.split("\n\n") if p.strip()]
    if not paras:
        return []
    chunks: list[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = (buf + "\n\n" + p).strip() if buf else p
        else:
            if buf:
                chunks.append(buf)
            if len(p) > max_chars:
                start = 0
                n = len(p)
                while start < n:
                    end = min(start + max_chars, n)
                    chunks.append(p[start:end])
                    if end >= n:
                        break
                    start = max(0, end - overlap)
                buf = ""
            else:
                buf = p
    if buf:
        chunks.append(buf)
    return chunks


def stable_chunk_id(repo_path: str, chunk_index: int) -> str:
    raw = f"core_canon|{repo_path}|{chunk_index}".encode("utf-8")
    return "cc_" + hashlib.sha256(raw).hexdigest()[:40]


def _rows_from_disk(root: Path) -> list[dict]:
    from src.scripts.sync_omega_canon_registry import _collect_entries

    rows_tuples = _collect_entries(root)
    out: list[dict] = []
    for repo_path, role, section, title, sha, size, _meta in rows_tuples:
        out.append(
            {
                "repo_path": repo_path,
                "document_role": role,
                "anchor_section": section,
                "title": title or "",
                "body_sha256": sha,
                "byte_size": int(size),
            }
        )
    return out


async def _fetch_pg_rows(limit: int) -> list[dict]:
    from src.db import event_store_client as esc

    return await esc.list_canon_documents(limit=limit)


def _read_repo_file(root: Path, repo_path: str) -> tuple[str, str | None]:
    p = root / repo_path
    if not p.is_file():
        return "", None
    try:
        body = p.read_bytes()
    except OSError:
        return "", None
    sha = hashlib.sha256(body).hexdigest()
    try:
        text = body.decode("utf-8", errors="replace")
    except Exception:
        return "", sha
    return text, sha


def ingest_canon_to_chroma(
    *,
    root: Path,
    rows: list[dict],
    dry_run: bool,
    max_chars: int,
    overlap: int,
    max_file_chars: int,
) -> tuple[int, list[str]]:
    """
    Returns (exit_code, messages). exit_code 0 = ok, 1 = hard fail, 2 = partial (warnings only).
    """
    from src.logic_core.crystal_grid_engine import CrystalGridEngine
    from src.network.chroma_client import (
        COLLECTION_CORE_CANON,
        _get_collection_sync,
        _get_embedding,
        is_configured,
    )

    if not is_configured():
        return 1, ["ChromaDB nicht konfiguriert (CHROMA_HOST oder CHROMA_LOCAL_PATH)."]

    warnings: list[str] = []
    col = _get_collection_sync(COLLECTION_CORE_CANON, create_if_missing=True)
    date_added = date.today().isoformat()
    total_chunks = 0

    for row in rows:
        repo_path = (row.get("repo_path") or "").strip()
        if not repo_path or not _is_text_canon_path(repo_path):
            continue
        text, disk_sha = _read_repo_file(root, repo_path)
        if not text:
            warnings.append(f"leer oder nicht lesbar: {repo_path}")
            continue
        if len(text) > max_file_chars:
            warnings.append(f"überspringe (>{max_file_chars} Zeichen): {repo_path}")
            continue
        pg_sha = (row.get("body_sha256") or "").strip()
        if disk_sha and pg_sha and disk_sha != pg_sha:
            warnings.append(f"SHA-Drift PG vs. Platte (ingest trotzdem): {repo_path}")

        if dry_run:
            chs = chunk_canon_text(text, max_chars, overlap)
            total_chunks += len(chs)
            continue

        try:
            prev = col.get(where={"repo_path": repo_path}, include=[])
            ids_del = prev.get("ids") or []
            if ids_del:
                col.delete(ids=ids_del)
        except Exception as e:
            warnings.append(f"Chroma delete für {repo_path}: {e}")

        chunks = chunk_canon_text(text, max_chars, overlap)
        if not chunks:
            continue

        doc_role = str(row.get("document_role") or "")
        anchor_sec = str(row.get("anchor_section") or "")
        title = (str(row.get("title") or "") or repo_path)[:300]
        body_sha = disk_sha or pg_sha or ""

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []
        embeddings: list[list[float]] = []

        for i, chunk in enumerate(chunks):
            cid = stable_chunk_id(repo_path, i)
            raw_emb = _get_embedding(chunk)
            _anchor_id, snapped = CrystalGridEngine.snap_to_grid(raw_emb)
            ids.append(cid)
            documents.append(chunk)
            metadatas.append(
                {
                    "type": "context",
                    "source_collection": "core_canon",
                    "source_file": repo_path,
                    "repo_path": repo_path,
                    "chunk_index": int(i),
                    "anchor_section": anchor_sec[:200],
                    "document_role": doc_role[:120],
                    "title": title,
                    "body_sha256": body_sha[:128],
                    "date_added": date_added,
                }
            )
            embeddings.append(snapped)

        try:
            col.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
            total_chunks += len(chunks)
        except Exception as e:
            warnings.append(f"Chroma add fehlgeschlagen {repo_path}: {e}")
            return 2, warnings + [f"[PARTIAL] {total_chunks} Chunks vor Abbruch."]

    if dry_run:
        return 0, [f"[dry-run] {total_chunks} Chunks für {len(rows)} Registry-Zeilen (textpfade)."]

    msg = [f"[OK] core_canon: {total_chunks} Chunks aus {len(rows)} Registry-Zeilen."]
    msg.extend(warnings)
    if total_chunks == 0:
        return 1, msg + ["[FAIL] keine Chunks geschrieben (Pfade leer, zu groß oder kein Text)."]
    return 0, msg


async def run_ingest_async(
    *,
    from_disk: bool,
    limit: int,
    dry_run: bool,
    max_chars: int,
    overlap: int,
    max_file_chars: int,
) -> int:
    root = _PROJECT_ROOT
    if from_disk:
        rows = _rows_from_disk(root)
    else:
        rows = await _fetch_pg_rows(limit)
        if not rows:
            rows = _rows_from_disk(root)
            print(
                "[INFO] PG leer oder nicht erreichbar — Fallback --from-disk (Anker/Seeds).",
                file=sys.stderr,
            )

    if not rows:
        print("[FAIL] keine Kanon-Zeilen.", file=sys.stderr)
        return 1

    code, msgs = ingest_canon_to_chroma(
        root=root,
        rows=rows,
        dry_run=dry_run,
        max_chars=max_chars,
        overlap=overlap,
        max_file_chars=max_file_chars,
    )
    for m in msgs:
        print(m, file=sys.stdout if code == 0 else sys.stderr)
    return 0 if code == 0 else code


async def ingest_from_pg_after_sync(root: Path | None = None) -> int:
    """Nach erfolgreichem sync_omega_canon_registry: nur PG, kein Fallback nötig."""
    root = root or _PROJECT_ROOT
    rows = await _fetch_pg_rows(500)
    if not rows:
        return 1
    code, msgs = ingest_canon_to_chroma(
        root=root,
        rows=rows,
        dry_run=False,
        max_chars=1600,
        overlap=120,
        max_file_chars=1_500_000,
    )
    for m in msgs:
        print(m, file=sys.stdout if code == 0 else sys.stderr)
    return 0 if code == 0 else code


def main() -> int:
    ap = argparse.ArgumentParser(description="Kanon → Chroma core_canon (Phase 2)")
    ap.add_argument("--from-disk", action="store_true", help="Anker/Seeds statt PG")
    ap.add_argument("--dry-run", action="store_true", help="Kein Chroma-Write, nur Zählen")
    ap.add_argument("--limit", type=int, default=500, help="PG list_canon_documents limit")
    ap.add_argument("--chunk-chars", type=int, default=1600, dest="chunk_chars")
    ap.add_argument("--chunk-overlap", type=int, default=120, dest="chunk_overlap")
    ap.add_argument("--max-file-chars", type=int, default=1_500_000, dest="max_file_chars")
    args = ap.parse_args()
    return asyncio.run(
        run_ingest_async(
            from_disk=args.from_disk,
            limit=args.limit,
            dry_run=args.dry_run,
            max_chars=args.chunk_chars,
            overlap=args.chunk_overlap,
            max_file_chars=args.max_file_chars,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
