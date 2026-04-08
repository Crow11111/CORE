#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH → VPS: curl Loopback-Health für Omega-Backend (systemd, Host-Port laut Vertrag).

Abnahme: Remote `bash -lc` mit `set -o pipefail` + curl gegen Loopback (sonst: fehlgeschlagenes curl + `head` = fälschlich Exit 0).
Keine Secrets.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=True)

from src.config.vps_public_ports import OMEGA_BACKEND_HOST_PORT


def _ssh_base(host: str, key: str | None) -> list[str]:
    import subprocess

    cmd: list[str] = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=20",
    ]
    if key:
        cmd.extend(["-i", key])
    cmd.append(f"root@{host}")
    return cmd


def _ssh_remote_shell(
    host: str,
    key: str | None,
    remote_line: str,
    *,
    capture_output: bool = False,
    text: bool = False,
):
    import subprocess

    return subprocess.run(
        _ssh_base(host, key) + [remote_line],
        capture_output=capture_output,
        text=text,
    )


def main() -> int:
    host = (os.getenv("VPS_HOST") or "").strip()
    key_raw = (os.getenv("VPS_SSH_KEY") or "").strip()
    if not host:
        print("[FAIL] VPS_HOST setzen", file=sys.stderr)
        return 1
    key: str | None = key_raw if key_raw else None
    if key:
        kp = Path(key)
        if not kp.is_file():
            print(f"[FAIL] VPS_SSH_KEY ungültig: {kp}", file=sys.stderr)
            return 1
        key = str(kp)

    port = int(OMEGA_BACKEND_HOST_PORT)
    # pipefail: ohne das liefert eine Pipeline mit fehlschlagendem curl Exit 0 (weil head zuletzt läuft).
    line = (
        f'bash -lc "set -o pipefail; curl -sf http://127.0.0.1:{port}/status | head -c 400"'
    )
    out = _ssh_remote_shell(host, key, line, capture_output=True, text=True)
    if out.stdout:
        sys.stdout.write(out.stdout)
    if out.stderr:
        sys.stderr.write(out.stderr)
    if out.returncode != 0:
        print(f"[FAIL] SSH/curl Exit {out.returncode}", file=sys.stderr)
        return 1
    print(f"[OK] omega-backend Loopback /status (Port {port})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
