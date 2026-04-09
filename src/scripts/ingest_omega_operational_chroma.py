#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ist-/Laufflächen-Dokumente → ChromaDB `core_operational` (getrennt von `core_canon` / Soll-Kanon).

Quelle: docs/00_STAMMDOKUMENTE/KERNARBEITER_SURFACE_PATHS.yaml (kuratierte repo_path + focus).
Siehe docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md

Usage:
  PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.scripts.ingest_omega_operational_chroma
  PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.scripts.ingest_omega_operational_chroma --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import date
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.scripts.ingest_omega_canon_chroma import (
    _is_text_canon_path,
    _read_repo_file,
    chunk_canon_text,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=True)

_DEFAULT_YAML = (
    _PROJECT_ROOT / "docs" / "00_STAMMDOKUMENTE" / "KERNARBEITER_SURFACE_PATHS.yaml"
)


def stable_operational_chunk_id(repo_path: str, chunk_index: int) -> str:
    raw = f"core_operational|{repo_path}|{chunk_index}".encode("utf-8")
    return "co_" + hashlib.sha256(raw).hexdigest()[:40]


def load_surface_rows(yaml_path: Path) -> list[dict]:
    if not yaml_path.is_file():
        raise FileNotFoundError(f"YAML fehlt: {yaml_path}")
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8", errors="replace")) or {}
    rows: list[dict] = []
    for item in data.get("paths") or []:
        if not isinstance(item, dict):
            continue
        rp = (item.get("repo_path") or "").strip()
        focus = (item.get("focus") or "").strip()
        if not rp or ".." in rp or rp.startswith("/"):
            continue
        rows.append(
            {
                "repo_path": rp,
                "document_role": "operational_surface",
                "anchor_section": focus[:200],
                "title": "",
                "body_sha256": "",
            }
        )
    return rows


def ingest_operational_to_chroma(
    *,
    root: Path,
    rows: list[dict],
    dry_run: bool,
    max_chars: int,
    overlap: int,
    max_file_chars: int,
) -> tuple[int, list[str]]:
    from src.logic_core.crystal_grid_engine import CrystalGridEngine
    from src.network.chroma_client import (
        COLLECTION_CORE_OPERATIONAL,
        _get_collection_sync,
        _get_embedding,
        is_configured,
    )

    if dry_run:
        total = 0
        for row in rows:
            rp = (row.get("repo_path") or "").strip()
            if not rp or not _is_text_canon_path(rp):
                continue
            text, _ = _read_repo_file(root, rp)
            if not text or len(text) > max_file_chars:
                continue
            total += len(chunk_canon_text(text, max_chars, overlap))
        return 0, [f"[dry-run] core_operational: {total} Chunks für {len(rows)} YAML-Pfade."]

    if not is_configured():
        return 1, ["ChromaDB nicht konfiguriert (CHROMA_HOST oder CHROMA_LOCAL_PATH)."]

    warnings: list[str] = []
    col = _get_collection_sync(COLLECTION_CORE_OPERATIONAL, create_if_missing=True)
    date_added = date.today().isoformat()
    total_chunks = 0

    for row in rows:
        repo_path = (row.get("repo_path") or "").strip()
        if not repo_path or not _is_text_canon_path(repo_path):
            warnings.append(f"überspringe (kein Textpfad): {repo_path}")
            continue
        text, disk_sha = _read_repo_file(root, repo_path)
        if not text:
            warnings.append(f"fehlt oder leer: {repo_path}")
            continue
        if len(text) > max_file_chars:
            warnings.append(f"überspringe (>{max_file_chars} Zeichen): {repo_path}")
            continue

        try:
            prev = col.get(where={"repo_path": repo_path}, include=[])
            ids_del = prev.get("ids") or []
            if ids_del:
                col.delete(ids=ids_del)
        except Exception as e:
            warnings.append(f"Chroma delete {repo_path}: {e}")

        chunks = chunk_canon_text(text, max_chars, overlap)
        if not chunks:
            continue

        focus = str(row.get("anchor_section") or "")[:200]
        body_sha = disk_sha or ""

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []
        embeddings: list[list[float]] = []

        for i, chunk in enumerate(chunks):
            cid = stable_operational_chunk_id(repo_path, i)
            raw_emb = _get_embedding(chunk)
            _aid, snapped = CrystalGridEngine.snap_to_grid(raw_emb)
            ids.append(cid)
            documents.append(chunk)
            metadatas.append(
                {
                    "type": "context",
                    "source_collection": "core_operational",
                    "layer": "operational_ist",
                    "source_file": repo_path,
                    "repo_path": repo_path,
                    "chunk_index": int(i),
                    "focus": focus,
                    "document_role": "operational_surface",
                    "body_sha256": (body_sha or "")[:128],
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

    msg = [f"[OK] core_operational: {total_chunks} Chunks aus {len(rows)} Surface-Pfaden."]
    msg.extend(warnings)
    if total_chunks == 0:
        return 1, msg + ["[FAIL] keine Chunks geschrieben."]
    return 0, msg


def main() -> int:
    ap = argparse.ArgumentParser(description="Ist-Surface → Chroma core_operational")
    ap.add_argument(
        "--yaml-path",
        type=Path,
        default=_DEFAULT_YAML,
        help="Pfad zu KERNARBEITER_SURFACE_PATHS.yaml",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--chunk-chars", type=int, default=1600, dest="chunk_chars")
    ap.add_argument("--chunk-overlap", type=int, default=120, dest="chunk_overlap")
    ap.add_argument("--max-file-chars", type=int, default=1_500_000, dest="max_file_chars")
    args = ap.parse_args()

    try:
        rows = load_surface_rows(args.yaml_path)
    except Exception as e:
        print(f"[FAIL] YAML: {e}", file=sys.stderr)
        return 1
    if not rows:
        print("[FAIL] keine Pfade in YAML.", file=sys.stderr)
        return 1

    code, msgs = ingest_operational_to_chroma(
        root=_PROJECT_ROOT,
        rows=rows,
        dry_run=args.dry_run,
        max_chars=args.chunk_chars,
        overlap=args.chunk_overlap,
        max_file_chars=args.max_file_chars,
    )
    for m in msgs:
        print(m, file=sys.stdout if code == 0 else sys.stderr)
    return 0 if code == 0 else code


if __name__ == "__main__":
    raise SystemExit(main())
