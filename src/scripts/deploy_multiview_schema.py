"""Deploy multi_view_embeddings schema to VPS pgvector via SSH."""
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

import subprocess

import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
except Exception:
    pass
SSH_KEY = os.getenv("VPS_SSH_KEY", "").strip() or r"/OMEGA_CORE\.ssh\id_ed25519_hostinger"
VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250").strip()
VPS_USER = os.getenv("VPS_USER", "root").strip()

SQL = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS multi_view_embeddings (
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

DOCKER_CMD = f"docker exec -i atlas_postgres_state psql -U atlas_admin -d atlas_state"
SSH_CMD = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
    "-i", SSH_KEY, f"{VPS_USER}@{VPS_HOST}", DOCKER_CMD
]

print(f"Deploying multi_view_embeddings schema to {VPS_HOST}...")
result = subprocess.run(SSH_CMD, input=SQL, capture_output=True, text=True, timeout=30)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
print(f"Exit code: {result.returncode}")
if result.returncode == 0:
    print("Schema deployed successfully.")
else:
    print("Schema deployment FAILED.")
    sys.exit(1)
