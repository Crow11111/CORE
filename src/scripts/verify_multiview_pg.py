#!/usr/bin/env python3
"""
Verifikation: SSH zum VPS + atlas_postgres_state + Tabelle multi_view_embeddings.
Exit 0 wenn erreichbar und Tabelle existiert. Liest .env (VPS_SSH_KEY, VPS_HOST).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
except Exception:
    pass


def main() -> int:
    from src.db.multi_view_client import _multiview_ssh_config

    key, host, user, docker_cmd = _multiview_ssh_config()
    if not key or not os.path.isfile(key):
        print("[FAIL] SSH-Key fehlt: VPS_SSH_KEY oder MULTIVIEW_SSH_KEY in .env")
        return 1
    sql = "SELECT COUNT(*)::text FROM multi_view_embeddings LIMIT 1;"
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=15", "-i", key, f"{user}@{host}",
        f'{docker_cmd} -c "{sql}"',
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=45)
    out = (r.stdout or b"").decode("utf-8", errors="replace")
    err = (r.stderr or b"").decode("utf-8", errors="replace")
    if r.returncode != 0:
        print("[FAIL] SSH/psql:", err or out or r.returncode)
        return 1
    print("[PASS] multi_view_embeddings erreichbar. Auszug:", out.strip()[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
