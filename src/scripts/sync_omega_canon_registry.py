#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synchronisiert OMEGA_RESONANCE_ANCHOR.md + referenzierte Repo-Pfade → omega_canon_documents (PostgreSQL).

Voraussetzung: Migration 001_omega_canon_documents.sql auf derselben DB wie omega_events angewendet.
Siehe docs/05_AUDIT_PLANNING/MIGRATIONPLAN_OMEGA_WISSEN_DBS.md

Usage:
  cd /OMEGA_CORE && PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.scripts.sync_omega_canon_registry
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=True)

ANCHOR_NAME = "OMEGA_RESONANCE_ANCHOR.md"

# Explizit aus Anker §4–§5 und Fußzeile (zusätzlich zur Zeilen-Heuristik).
STATIC_SEEDS: list[tuple[str, str, str]] = [
    (ANCHOR_NAME, "anchor_root", "0"),
    (".cursorrules", "referenced", "3"),
    ("CORE_EICHUNG.md", "referenced", "footer"),
    ("docs/SYSTEM_CODEX.md", "referenced", "footer"),
    ("docs/05_AUDIT_PLANNING/TICKET_9_GIT_RESONANCE.md", "referenced", "5"),
    ("run_vollkreis_abnahme.py", "executable", "4"),
    ("omega_core.py", "executable", "4"),
    ("src/ai/model_registry.py", "code", "4"),
    ("src/daemons/dread_membrane_daemon.py", "code", "5"),
    (
        "docs/05_AUDIT_PLANNING/MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md",
        "referenced",
        "4",
    ),
    (
        "docs/05_AUDIT_PLANNING/O2_AUDIT_KETTEN_KOHAERENZ_2026-04-06.md",
        "referenced",
        "4",
    ),
]

_BACKTICK = re.compile(r"`([^`]+\.(?:md|py|mdc|sql|yaml|yml|tsx?|json))`")
_DOCS_PATH = re.compile(r"\b(docs/[\w./\-]+\.md)\b")
_SECTION = re.compile(r"^##\s+(\d+|[\d.]+)\s")


def _sql_str(s: str | None) -> str:
    if s is None:
        return "NULL"
    return "'" + (s or "").replace("'", "''") + "'"


def _title_from_file(p: Path) -> str:
    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    for line in raw.splitlines()[:12]:
        t = line.strip()
        if t.startswith("# "):
            return t[2:].strip()[:500]
        if t.startswith("## ") and not t.startswith("###"):
            return t[3:].strip()[:500]
    return ""


def _parse_anchor_paths(anchor_text: str) -> dict[str, tuple[str, str]]:
    """repo_path -> (document_role, anchor_section)."""
    out: dict[str, tuple[str, str]] = {}
    current_section = "prose"
    for line in anchor_text.splitlines():
        msec = _SECTION.match(line.strip())
        if msec:
            current_section = msec.group(1)
        for m in _BACKTICK.finditer(line):
            rel = m.group(1).strip()
            if not rel or ".." in rel or rel.startswith("/"):
                continue
            if "*" in rel or "?" in rel:
                continue
            if rel.endswith((".md", ".py")) and "/" not in rel and rel not in ("omega_core.py",):
                if rel.startswith("*"):
                    continue
            out.setdefault(rel, ("referenced", current_section))
        for m in _DOCS_PATH.finditer(line):
            rel = m.group(1).strip()
            out.setdefault(rel, ("referenced", current_section))
    return out


def _collect_entries(root: Path) -> list[tuple[str, str, str, str, str, int, dict]]:
    anchor_path = root / ANCHOR_NAME
    if not anchor_path.is_file():
        print(f"[FAIL] {ANCHOR_NAME} fehlt unter {root}", file=sys.stderr)
        raise SystemExit(1)
    anchor_text = anchor_path.read_text(encoding="utf-8", errors="replace")

    merged: dict[str, tuple[str, str]] = {}
    for path, role, sec in STATIC_SEEDS:
        merged[path] = (role, sec)
    merged.update(_parse_anchor_paths(anchor_text))

    if (root / ANCHOR_NAME).is_file():
        merged.pop("docs/00_STAMMDOKUMENTE/OMEGA_RESONANCE_ANCHOR.md", None)

    rows: list[tuple[str, str, str, str, str, int, dict]] = []
    for repo_path, (role, section) in sorted(merged.items()):
        p = root / repo_path
        if not p.is_file():
            print(f"[--] überspringe (fehlt): {repo_path}", file=sys.stderr)
            continue
        body = p.read_bytes()
        sha = hashlib.sha256(body).hexdigest()
        size = len(body)
        title = _title_from_file(p)
        meta: dict = {"sync_script": "sync_omega_canon_registry"}
        rows.append((repo_path, role, section, title, sha, size, meta))
    return rows


def _upsert_sql(
    repo_path: str,
    role: str,
    section: str,
    title: str,
    sha: str,
    size: int,
    meta: dict,
) -> str:
    meta_json = json.dumps(meta, ensure_ascii=False).replace("'", "''")
    return f"""
INSERT INTO omega_canon_documents (repo_path, document_role, anchor_section, title, body_sha256, byte_size, metadata)
VALUES (
  {_sql_str(repo_path)},
  {_sql_str(role)},
  {_sql_str(section)},
  {_sql_str(title) if title else "NULL"},
  {_sql_str(sha)},
  {int(size)},
  '{meta_json}'::jsonb
)
ON CONFLICT (repo_path) DO UPDATE SET
  document_role = EXCLUDED.document_role,
  anchor_section = EXCLUDED.anchor_section,
  title = EXCLUDED.title,
  body_sha256 = EXCLUDED.body_sha256,
  byte_size = EXCLUDED.byte_size,
  last_synced_at = CURRENT_TIMESTAMP,
  metadata = omega_canon_documents.metadata || EXCLUDED.metadata;
""".strip()


_MIGRATION_FILE = _PROJECT_ROOT / "src" / "db" / "migrations" / "001_omega_canon_documents.sql"


async def _ensure_canon_table() -> tuple[bool, str | None]:
    """Idempotentes DDL (CREATE IF NOT EXISTS) — gleicher Weg wie omega_events."""
    from src.db.multi_view_client import _run_pg_sql

    if not _MIGRATION_FILE.is_file():
        return False, f"migration file missing: {_MIGRATION_FILE}"
    ddl = _MIGRATION_FILE.read_text(encoding="utf-8", errors="replace")
    # Kommentare und Leerzeilen für psql ok; ein Statement-Block
    ok, out = await _run_pg_sql(ddl.strip(), timeout=60)
    if not ok:
        return False, out or "ddl_failed"
    return True, None


async def _run_all(rows: list[tuple[str, str, str, str, str, int, dict]]) -> tuple[int, str | None]:
    from src.db.multi_view_client import _run_pg_sql

    errors: list[str] = []
    for repo_path, role, section, title, sha, size, meta in rows:
        sql = _upsert_sql(repo_path, role, section, title, sha, size, meta)
        ok, out = await _run_pg_sql(sql, timeout=45)
        if not ok:
            errors.append(f"{repo_path}: {out or '?'}"[:500])
    if errors:
        return 0, "; ".join(errors[:5])
    return len(rows), None


async def main_async() -> int:
    ok_ddl, ddl_err = await _ensure_canon_table()
    if not ok_ddl:
        print(f"[FAIL] DDL omega_canon_documents: {ddl_err}", file=sys.stderr)
        return 1
    rows = _collect_entries(_PROJECT_ROOT)
    if not rows:
        print("[FAIL] keine Dateien zum Sync (alle Pfade fehlen?)", file=sys.stderr)
        return 1
    n, err = await _run_all(rows)
    if err:
        print(f"[FAIL] PG upsert: {err}", file=sys.stderr)
        return 1
    print(f"[OK] omega_canon_documents: {n} Zeilen synchronisiert.")
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
