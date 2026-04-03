# -*- coding: utf-8 -*-
"""
TICKET_10 (Phase 3): Agenten-Autarkie (WhatsApp Pairing)
Führt autonom den Login-Prozess im openclaw-admin Container auf dem VPS aus
und streamt den QR-Code ins Terminal.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

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

    if not host or not user or not key:
        print("ERROR: SSH Credentials missing in .env")
        exit(1)

    key_path = Path(key).expanduser()

    return [
        "ssh",
        "-o",
        "StrictHostKeyChecking=yes",
        "-i",
        str(key_path),
        "-p",
        str(port),
        "-t", # Force pseudo-tty to ensure QR code renders correctly with ANSI
        f"{user}@{host}",
    ]


def run_whatsapp_login() -> None:
    print("Starte WhatsApp Pairing Session auf VPS...")
    print("Bitte halte dein Smartphone bereit, um den QR-Code zu scannen.\n")

    cmd = _ssh_base_args() + ["docker exec -it openclaw-admin openclaw channels login whatsapp"]

    try:
        # Popen without capture_output connects stdout directly to our terminal
        # This is critical for the QR code to render correctly.
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[VETO] Fehler beim WhatsApp Pairing (Exit Code {e.returncode}).")
    except Exception as e:
        print(f"\n[VETO] Unerwarteter Fehler: {e}")


if __name__ == "__main__":
    run_whatsapp_login()
