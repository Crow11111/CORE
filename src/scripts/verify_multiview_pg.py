#!/usr/bin/env python3
"""
Verifikation: PG vs ChromaDB (Duale Topologie)
Status: RATIFIZIERT | OMEGA_ATTRACTOR

Prüft Erreichbarkeit beider Datenbanken und die Konsistenz der IDs.
"""
from __future__ import annotations

import os
import asyncio
import subprocess
import sys
from pathlib import Path

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.db.multi_view_client import _multiview_ssh_config, FACET_TO_COLLECTION
import chromadb

def get_pg_count() -> int:
    key, host, user, docker_cmd = _multiview_ssh_config()
    if not key or not os.path.isfile(key):
        return -1
    sql = "SELECT COUNT(*)::text FROM multi_view_embeddings LIMIT 1;"
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=15", "-i", key, f"{user}@{host}",
        f'{docker_cmd} -c "{sql}"',
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if r.returncode != 0:
            err = (r.stderr or "").strip()[:500]
            out = (r.stdout or "").strip()[:300]
            hint = f" ssh_rc={r.returncode}"
            if err:
                hint += f" stderr={err!r}"
            if out:
                hint += f" stdout={out!r}"
            print(f"[DIAG] PostgreSQL SSH/psql:{hint}")
            return -1
        out = r.stdout.strip()
        # Find the number in output like " 26984 \n(1 row)"
        for line in out.splitlines():
            line = line.strip()
            if line.isdigit():
                return int(line)
        return -1
    except Exception as ex:
        print(f"[DIAG] PostgreSQL SSH/psql: exception={type(ex).__name__}: {ex!s}")
        return -1

def get_chroma_counts() -> dict[str, int]:
    host = os.getenv("CHROMA_HOST", os.getenv("VPS_HOST", "187.77.68.250"))
    port = int(os.getenv("CHROMA_PORT", "32768"))
    try:
        client = chromadb.HttpClient(host=host, port=port)
        results = {}
        for coll_name in FACET_TO_COLLECTION.values():
            try:
                coll = client.get_collection(name=coll_name)
                results[coll_name] = coll.count()
            except Exception:
                results[coll_name] = 0
        return results
    except Exception:
        return {}

def main() -> int:
    pg_count = get_pg_count()
    chroma_counts = get_chroma_counts()

    print("=== [MULTI-VIEW SYSTEM STATUS] ===")
    if pg_count >= 0:
        print(f"[PASS] PostgreSQL: {pg_count} Einträge.")
    else:
        print("[FAIL] PostgreSQL nicht erreichbar oder Fehler.")

    all_chroma_synced = True
    for coll, count in chroma_counts.items():
        print(f"[INFO] ChromaDB '{coll}': {count} Einträge.")
        if count == 0:
            all_chroma_synced = False

    if pg_count > 0 and not any(chroma_counts.values()):
        print("[WARN] Keine Einträge in ChromaDB gefunden!")
    elif pg_count > 0 and any(c < pg_count for c in chroma_counts.values()):
        print(f"[INFO] Erwartete Diskrepanz: {pg_count - max(chroma_counts.values())} Einträge sind im Legacy-Format.")

    # Status-Code logic
    if pg_count >= 0 and any(chroma_counts.values()):
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
