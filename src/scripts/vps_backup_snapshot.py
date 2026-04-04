#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPS: Backup-Snapshot vor riskanten Kong-/Infra-Änderungen.

Schreibt auf dem VPS unter /root/omega-core-backups/<UTC>/ u. a. Kong-Admin-Exporte
und docker ps. Nutzung: python -m src.scripts.vps_backup_snapshot

Siehe docs/05_AUDIT_PLANNING/VPS_UMSETZUNGSPLAN_BACKUP_KONG_HEALTH.md
"""
from __future__ import annotations

import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env", override=True)

VPS_HOST = (os.getenv("VPS_HOST") or "").strip() or "187.77.68.250"
VPS_SSH_KEY = (os.getenv("VPS_SSH_KEY") or "").strip() or "/home/mth/.ssh/id_ed25519_hostinger"


REMOTE_BASH = r"""
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
BK=/root/omega-core-backups/$TS
mkdir -p "$BK/compose"
docker ps -a >"$BK/docker_ps.txt" 2>&1 || true
curl -sS --connect-timeout 5 "http://127.0.0.1:32777/services" >"$BK/kong_services.json" 2>&1 || echo '{"data":[]}' >"$BK/kong_services.json"
curl -sS --connect-timeout 5 "http://127.0.0.1:32777/routes" >"$BK/kong_routes.json" 2>&1 || echo '{"data":[]}' >"$BK/kong_routes.json"
curl -sS --connect-timeout 5 "http://127.0.0.1:32777/plugins" >"$BK/kong_plugins.json" 2>&1 || echo '{"data":[]}' >"$BK/kong_plugins.json"
for pair in \
  "/docker/kong-s7rk/docker-compose.yml:compose/kong-s7rk.docker-compose.yml" \
  "/docker/chroma-uvmy/docker-compose.yml:compose/chroma-uvmy.docker-compose.yml" \
  "/docker/evolution-api-yxa5/docker-compose.yml:compose/evolution-api-yxa5.docker-compose.yml" \
  "/opt/atlas-core/mcp-server/docker-compose.yml:compose/mcp-server.docker-compose.yml"
do
  src="${pair%%:*}"
  dst="${pair##*:}"
  if test -f "$src"; then cp -a "$src" "$BK/$dst"; fi
done
echo "$TS Backup-Verzeichnis: $BK" | tee "$BK/README.txt"
echo "$BK"
"""


def main() -> int:
    ssh_cmd = [
        "ssh",
        "-o",
        "ConnectTimeout=15",
        "-o",
        "BatchMode=yes",
        "-i",
        VPS_SSH_KEY,
        f"root@{VPS_HOST}",
        "bash",
        "-s",
    ]
    r = subprocess.run(
        ssh_cmd,
        input=REMOTE_BASH,
        capture_output=True,
        text=True,
        timeout=120,
    )
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    if r.returncode != 0:
        print("[FAIL] SSH-Backup exit=", r.returncode, file=sys.stderr)
        if err:
            print(err[:800], file=sys.stderr)
        if out:
            print(out[:800], file=sys.stderr)
        return 1
    last = out.splitlines()[-1] if out else ""
    print("[OK] VPS-Backup abgeschlossen.")
    if last.startswith("/root/omega-core-backups/"):
        print("     Pfad:", last)
    return 0


if __name__ == "__main__":
    sys.exit(main())
