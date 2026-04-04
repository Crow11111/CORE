#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zero-Trust: rsync src/ → VPS /opt/omega-core-mirror, systemd Service+Timer installieren.

Voraussetzung: VPS_SSH_KEY, VPS_HOST in Umgebung (oder .env im Projektroot).
Keine Secrets im Log.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

MIRROR = "/opt/omega-core-mirror"
SERVICE = "omega-core-anti-heroin.service"
TIMER = "omega-core-anti-heroin.timer"


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    """
    Projekt-.env muss VPS_* setzen dürfen, auch wenn die IDE eine leere
    VPS_SSH_KEY exportiert (dotenv override=False würde dann NICHT aus .env laden).
    Gleiche Linie wie verify_vps_stack.py (override=True).
    """
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


def _ssh_remote_shell(host: str, key: str | None, remote_line: str, **kwargs: object) -> subprocess.CompletedProcess[str]:
    """
    Führt genau *ein* Remote-Kommando wie in der interaktiven Form
    ``ssh root@host 'mkdir -p … && …'`` aus.

    OpenSSH setzt die argv-Teile nach dem Host zu *einer* Command-Zeile zusammen.
    ``['sh', '-c', 'mkdir -p /x && y']`` wird dabei zu ``sh -c mkdir -p /x && y``;
    dann ist das Argument von ``-c`` nur ``mkdir`` → ``mkdir: missing operand``.
    """
    return subprocess.run(_ssh_base(host, key) + [remote_line], **kwargs)  # type: ignore[arg-type]


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
    if not src.is_dir():
        print("[FAIL] src/ fehlt", file=sys.stderr)
        return 1

    unit_dir = project / "infra" / "vps" / "systemd"
    svc = unit_dir / SERVICE
    tim = unit_dir / TIMER
    if not svc.is_file() or not tim.is_file():
        print("[FAIL] systemd-Unit-Dateien fehlen unter infra/vps/systemd/", file=sys.stderr)
        return 1

    mk = subprocess.run(
        _ssh_base(host, key) + ["mkdir", "-p", MIRROR + "/src"],
    )
    if mk.returncode != 0:
        print("[FAIL] mkdir auf VPS", file=sys.stderr)
        return 1

    remote = f"root@{host}:{MIRROR}/"
    print(f"[INFO] rsync src/ → {remote}src/")
    ssh_e = "ssh -o BatchMode=yes -o ConnectTimeout=20"
    if key:
        ssh_e += f" -i {shlex.quote(key)}"
    rsync_cmd = ["rsync", "-az", "--delete", "-e", ssh_e, f"{src}/", remote + "src/"]
    r = subprocess.run(rsync_cmd, cwd=str(project))
    if r.returncode != 0:
        print("[FAIL] rsync", file=sys.stderr)
        return 1

    for local, remote_path in (
        (svc, f"/etc/systemd/system/{SERVICE}"),
        (tim, f"/etc/systemd/system/{TIMER}"),
    ):
        print(f"[INFO] scp {local.name} → {remote_path}")
        c = subprocess.run(
            _scp_base(host, key) + [str(local), f"root@{host}:{remote_path}"]
        )
        if c.returncode != 0:
            print(f"[FAIL] scp {local.name}", file=sys.stderr)
            return 1

    env_line = f"OMEGA_MIRROR_ROOT={MIRROR}"
    wr = subprocess.run(
        _ssh_base(host, key)
        + [
            "sh",
            "-c",
            f"echo {shlex.quote(env_line)} > /etc/default/omega-core-anti-heroin",
        ]
    )
    if wr.returncode != 0:
        print("[FAIL] /etc/default/omega-core-anti-heroin", file=sys.stderr)
        return 1

    boot = subprocess.run(
        _ssh_base(host, key)
        + [
            "sh",
            "-c",
            "mkdir -p /var/log && touch /var/log/omega-core-anti-heroin.log "
            "&& chmod 644 /var/log/omega-core-anti-heroin.log "
            "&& systemctl daemon-reload "
            f"&& systemctl enable {TIMER} "
            f"&& systemctl start {TIMER} "
            f"&& systemctl start {SERVICE} "
            f"&& systemctl is-enabled {TIMER}",
        ],
    )
    if boot.returncode != 0:
        print("[FAIL] systemctl enable/start", file=sys.stderr)
        return 1

    out = subprocess.run(
        _ssh_base(host, key)
        + [
            "sh",
            "-c",
            f"/usr/bin/python3 {MIRROR}/src/scripts/run_anti_heroin_scan.py --root {MIRROR}; echo EXIT=$?",
        ],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(out.stdout or "")
    if out.stderr:
        sys.stderr.write(out.stderr)
    if out.returncode != 0 or "EXIT=0" not in (out.stdout or ""):
        print("[FAIL] Anti-Heroin-Lauf auf VPS nicht Exit 0", file=sys.stderr)
        return 1

    print("[PASS] VPS: Spiegel + systemd timer + Scan Exit 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
