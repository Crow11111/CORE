# -*- coding: utf-8 -*-
"""
OpenClaw VPS: SSH-gestützter Docker-Restart (spine + admin) mit Out-of-Band-Gateway-Check.
TICKET_10: StrictHostKeyChecking=yes, TrustCollapse bei SSH-Fehler oder fehlgeschlagener Verifikation.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

from src.logic_core.anti_heroin_validator import TrustCollapseException
from src.network import openclaw_client

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_env() -> None:
    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv()


def _ssh_base_args() -> list[str]:
    _load_env()
    host = os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST", "")
    user = os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER", "root")
    key = os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY", "")
    port_s = (os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or "").strip() or "22"
    try:
        port = int(port_s)
    except ValueError:
        port = 22

    if not host or not user:
        raise TrustCollapseException(
            "OpenClaw heal: SSH — VPS host/user missing in .env (OPENCLAW_ADMIN_VPS_* / VPS_*)"
        )
    if not key:
        raise TrustCollapseException(
            "OpenClaw heal: SSH — key path missing (OPENCLAW_ADMIN_VPS_SSH_KEY / VPS_SSH_KEY)"
        )
    key_path = Path(key).expanduser()
    if not key_path.is_file():
        raise TrustCollapseException(
            f"OpenClaw heal: SSH — key file not found (verify OPENCLAW_ADMIN_VPS_SSH_KEY / VPS_SSH_KEY): {key_path}"
        )

    return [
        "ssh",
        "-o",
        "StrictHostKeyChecking=yes",
        "-o",
        "BatchMode=yes",
        "-i",
        str(key_path),
        "-p",
        str(port),
        f"{user}@{host}",
    ]


def _run_remote_docker_restart() -> subprocess.CompletedProcess[str]:
    remote = "docker restart openclaw-spine openclaw-admin"
    cmd = _ssh_base_args() + [remote]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def execute_openclaw_vps_heal_cycle() -> None:
    """
    Startet openclaw-spine und openclaw-admin auf dem VPS per SSH neu, verifiziert danach check_gateway().
    """
    proc = _run_remote_docker_restart()
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise TrustCollapseException(
            f"OpenClaw heal: SSH/docker restart failed (exit {proc.returncode}): {err}"
        )

    ok, msg = openclaw_client.check_gateway()
    if not ok:
        raise TrustCollapseException(
            f"OpenClaw heal: gateway verify failed after restart — {msg}"
        )
