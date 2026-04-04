#!/usr/bin/env python3
"""
Migriert multi_view_embeddings auf vector(3072) (Gemini Embedding API liefert 3072 dim).
WARNUNG: Leert die Tabelle. Nur ausfuehren wenn Backup ok oder Tabelle leer/Test.
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

from src.db.multi_view_client import _multiview_ssh_config

SQL = """
DROP TABLE IF EXISTS multi_view_embeddings;
CREATE TABLE multi_view_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id VARCHAR(128) NOT NULL,
    document TEXT NOT NULL,
    source_collection VARCHAR(64),
    v_math     vector(3072),
    v_physics  vector(3072),
    v_philo    vector(3072),
    v_bio      vector(3072),
    v_info     vector(3072),
    v_narr     vector(3072),
    convergence_score FLOAT,
    convergence_pairs JSONB,
    e6_anchor_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_mv_doc_id ON multi_view_embeddings (doc_id);
CREATE INDEX IF NOT EXISTS idx_mv_convergence ON multi_view_embeddings (convergence_score DESC);
CREATE INDEX IF NOT EXISTS idx_mv_source ON multi_view_embeddings (source_collection);
"""


def main() -> int:
    key, host, user, docker_cmd = _multiview_ssh_config()
    if not key or not os.path.isfile(key):
        print("[FAIL] VPS_SSH_KEY fehlt")
        return 1
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=20",
        "-i", key, f"{user}@{host}", docker_cmd,
    ]
    r = subprocess.run(cmd, input=SQL.encode("utf-8"), capture_output=True, timeout=60)
    err = (r.stderr or b"").decode("utf-8", errors="replace")
    out = (r.stdout or b"").decode("utf-8", errors="replace")
    print(out)
    if err:
        print(err, file=sys.stderr)
    if r.returncode != 0:
        print("[FAIL] Migration")
        return 1
    print("[PASS] multi_view_embeddings jetzt vector(3072)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
