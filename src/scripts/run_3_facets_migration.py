#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/OMEGA_CORE")

from src.db.multi_view_client import _multiview_ssh_config

def run_migration():
    key, host, user, docker_cmd = _multiview_ssh_config()
    sql_path = "/OMEGA_CORE/src/scripts/migrate_to_3_facets.sql"

    with open(sql_path, "r") as f:
        sql = f.read()

    # Quote SQL for shell
    sql_escaped = sql.replace('"', '\\"')

    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-i", key, f"{user}@{host}",
        f"{docker_cmd} -c \"{sql_escaped}\""
    ]

    print(f"Running migration on {host}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Migration successful:")
        print(result.stdout)
    else:
        print("Migration failed:")
        print(result.stderr or result.stdout)
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
