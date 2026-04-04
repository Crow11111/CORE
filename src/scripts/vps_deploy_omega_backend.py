#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy: rsync src/ + requirements.txt → VPS /opt/omega-backend, venv, pip, systemd.

Ein Weg: rsync (kein git pull auf dem VPS). Siehe docs/03_INFRASTRUCTURE/OMEGA_BACKEND_VPS_SYSTEMD.md.

Voraussetzung: VPS_HOST, optional VPS_SSH_KEY in .env (override=True wie Spiegel-Deploy).
Keine Secrets im Log.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

from src.config.vps_public_ports import OMEGA_BACKEND_HOST_PORT

BACKEND_ROOT = "/opt/omega-backend"
SERVICE = "omega-backend.service"
UNIT_NAME = "omega-backend"


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(_root() / ".env", override=True)
    except ImportError:
        pass


def _ssh_base(host: str, key: str | None) -> list[str]:
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


def _scp_base(host: str, key: str | None) -> list[str]:
    cmd = ["scp", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20"]
    if key:
        cmd.extend(["-i", key])
    return cmd


def _ssh_remote_shell(
    host: str,
    key: str | None,
    remote_line: str,
    *,
    capture_output: bool = False,
    text: bool = False,
) -> subprocess.CompletedProcess:
    """Genau ein Remote-String pro SSH-Aufruf (kein kaputtes sh -c-Argv)."""
    return subprocess.run(
        _ssh_base(host, key) + [remote_line],
        capture_output=capture_output,
        text=text,
    )


def main() -> int:
    _load_dotenv()
    host = (os.getenv("VPS_HOST") or "").strip()
    key_raw = (os.getenv("VPS_SSH_KEY") or "").strip()
    if not host:
        print("[FAIL] VPS_HOST setzen (.env oder Export)", file=sys.stderr)
        return 1
    key: str | None = key_raw if key_raw else None
    if key:
        key_path = Path(key)
        if not key_path.is_file():
            print(f"[FAIL] VPS_SSH_KEY-Pfad ungültig: {key_path}", file=sys.stderr)
            return 1
        key = str(key_path)

    project = _root()
    src = project / "src"
    req = project / "requirements.txt"
    if not src.is_dir():
        print("[FAIL] src/ fehlt", file=sys.stderr)
        return 1
    if not req.is_file():
        print("[FAIL] requirements.txt fehlt", file=sys.stderr)
        return 1

    unit_dir = project / "infra" / "vps" / "systemd"
    svc = unit_dir / SERVICE
    env_tpl = unit_dir / "omega-backend.env.template"
    if not svc.is_file():
        print("[FAIL] systemd-Unit fehlt: infra/vps/systemd/" + SERVICE, file=sys.stderr)
        return 1
    if not env_tpl.is_file():
        print("[FAIL] omega-backend.env.template fehlt", file=sys.stderr)
        return 1

    mk = _ssh_remote_shell(host, key, f"mkdir -p {shlex.quote(BACKEND_ROOT)}/src")
    if mk.returncode != 0:
        print("[FAIL] mkdir auf VPS", file=sys.stderr)
        return 1

    remote = f"root@{host}:{BACKEND_ROOT}/"
    ssh_e = "ssh -o BatchMode=yes -o ConnectTimeout=20"
    if key:
        ssh_e += f" -i {shlex.quote(key)}"
    print(f"[INFO] rsync src/ → {remote}src/")
    rsync_src = subprocess.run(
        ["rsync", "-az", "--delete", "-e", ssh_e, f"{src}/", remote + "src/"],
        cwd=str(project),
    )
    if rsync_src.returncode != 0:
        print("[FAIL] rsync src/", file=sys.stderr)
        return 1

    print(f"[INFO] rsync requirements.txt → {remote}")
    rsync_req = subprocess.run(
        ["rsync", "-az", "-e", ssh_e, str(req), remote],
        cwd=str(project),
    )
    if rsync_req.returncode != 0:
        print("[FAIL] rsync requirements.txt", file=sys.stderr)
        return 1

    print(f"[INFO] scp {SERVICE} → /etc/systemd/system/")
    c1 = subprocess.run(
        _scp_base(host, key) + [str(svc), f"root@{host}:/etc/systemd/system/{SERVICE}"]
    )
    if c1.returncode != 0:
        print("[FAIL] scp unit", file=sys.stderr)
        return 1

    print("[INFO] scp omega-backend.env.template → /etc/default/omega-backend")
    c2 = subprocess.run(
        _scp_base(host, key)
        + [str(env_tpl), "root@{0}:/etc/default/omega-backend".format(host)]
    )
    if c2.returncode != 0:
        print("[FAIL] scp env template", file=sys.stderr)
        return 1

    venv_line = (
        f"cd {BACKEND_ROOT} && "
        "(test -d .venv || python3 -m venv .venv) && "
        ".venv/bin/pip install -U pip && "
        ".venv/bin/pip install -r requirements.txt"
    )
    pip = _ssh_remote_shell(host, key, venv_line)
    if pip.returncode != 0:
        print("[FAIL] venv/pip auf VPS", file=sys.stderr)
        return 1

    boot_line = (
        "systemctl daemon-reload && "
        f"systemctl enable {UNIT_NAME} && "
        f"systemctl restart {UNIT_NAME} && "
        f"systemctl is-active {UNIT_NAME}"
    )
    boot = _ssh_remote_shell(host, key, boot_line)
    if boot.returncode != 0:
        print("[FAIL] systemctl enable/restart", file=sys.stderr)
        return 1

    port = int(OMEGA_BACKEND_HOST_PORT)
    if (os.getenv("OMEGA_DEPLOY_SKIP_HEALTH") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        print("[INFO] Health-Check übersprungen (OMEGA_DEPLOY_SKIP_HEALTH)")
    else:
        health_line = (
            f"curl -sf http://127.0.0.1:{port}/status >/dev/null && echo CURL_OK || echo CURL_FAIL"
        )
        hc = _ssh_remote_shell(host, key, health_line, capture_output=True, text=True)
        sys.stdout.write(hc.stdout or "")
        if hc.stderr:
            sys.stderr.write(hc.stderr)
        if hc.returncode != 0 or "CURL_OK" not in (hc.stdout or ""):
            print(
                f"[FAIL] Health-Check curl 127.0.0.1:{port}/status "
                "(Dienst/.env auf VPS prüfen oder OMEGA_DEPLOY_SKIP_HEALTH=1).",
                file=sys.stderr,
            )
            return 1

    print("[PASS] VPS: Omega-Backend deploy + systemd aktiv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
