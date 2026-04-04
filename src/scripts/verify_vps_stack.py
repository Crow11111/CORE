#!/usr/bin/env python3
"""
VPS-Stack-Verifikation: Container-Status, Chroma v2 Heartbeat, optionale Knoten (Evolution, Monica, Kong).
Siehe docs/BIBLIOTHEK_KERN_DOKUMENTE.md, docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md, VPS_KNOTEN_UND_FLUSSE.md.
"""
import os
import subprocess
import sys
import httpx
from dotenv import load_dotenv

from src.config.vps_public_ports import (
    CHROMA_UVMY_HOST_PORT,
    EVOLUTION_API_HOST_PORT,
    KONG_ADMIN_API_HOST_PORT,
    MONICA_HTTP_HOST_PORT,
)

load_dotenv("/OMEGA_CORE/.env", override=True)

VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250")
VPS_SSH_KEY = os.getenv("VPS_SSH_KEY", "/home/mth/.ssh/id_ed25519_hostinger")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", str(CHROMA_UVMY_HOST_PORT)))
EVOLUTION_API_URL = (os.getenv("EVOLUTION_API_URL") or "").strip() or (
    f"http://{VPS_HOST}:{EVOLUTION_API_HOST_PORT}"
)
MONICA_URL = (os.getenv("MONICA_URL") or "").strip() or (
    f"http://{VPS_HOST}:{MONICA_HTTP_HOST_PORT}"
)
KONG_ADMIN_URL = (os.getenv("KONG_ADMIN_URL") or "").strip() or (
    f"http://{VPS_HOST}:{KONG_ADMIN_API_HOST_PORT}"
)

def run_ssh(cmd: str) -> tuple[int, str]:
    full = f'ssh -o ConnectTimeout=15 -o BatchMode=yes -i "{VPS_SSH_KEY}" root@{VPS_HOST} "{cmd}"'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=45)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def _container_up(lines: list[str], substring: str) -> bool:
    return any(substring in l and "Up" in l for l in lines)

def main():
    ok = True
    # 1) Docker ps – Pflicht-Container
    code, out = run_ssh("docker ps --format '{{.Names}} {{.Status}}'")
    if code != 0:
        print("[FAIL] VPS SSH oder docker ps:", out[:400])
        ok = False
    else:
        lines = [l for l in out.strip().split("\n") if l]
        expected = ["openclaw-admin", "chroma-uvmy-chromadb", "mcp-server", "ha-atlas"]
        for name in expected:
            if _container_up(lines, name):
                print(f"[OK] {name}")
            else:
                print(f"[WARN] {name} nicht Up oder fehlt")
                ok = False
        # Optionale VPS-Knoten (nur Hinweis, kein ok=False)
        for label, sub in [("evolution-api", "evolution"), ("monica", "monica"), ("kong", "kong")]:
            if _container_up(lines, sub):
                print(f"[OK] (optional) {label}")
            else:
                print(f"[--] (optional) {label} nicht gefunden")
        print(f"  Container gesamt: {len(lines)}")
    # 2) Chroma v2 heartbeat
    try:
        r = httpx.get(
            f"http://{VPS_HOST}:{CHROMA_PORT}/api/v2/heartbeat",
            timeout=15.0,
        )
        if r.status_code == 200 and "heartbeat" in r.text:
            print("[OK] Chroma v2 heartbeat")
        else:
            print("[FAIL] Chroma v2:", r.status_code, r.text[:200])
            ok = False
    except Exception as e:
        print("[FAIL] Chroma v2:", e)
        ok = False
    # 3) Optionale HTTP-Checks (Evolution, Monica, Kong) – nur Hinweis, kein Fail
    for url, kind in [
        (EVOLUTION_API_URL, "Evolution API"),
        (MONICA_URL, "Monica"),
        (KONG_ADMIN_URL, "Kong"),
    ]:
        try:
            u = url.strip().rstrip("/") or "http://localhost"
            r = httpx.get(u, timeout=3.0)
            if r.status_code in (200, 301, 302, 401, 404):
                print(f"[OK] (optional) {kind} erreichbar")
            else:
                print(f"[--] (optional) {kind} HTTP {r.status_code}")
        except Exception:
            print(f"[--] (optional) {kind} nicht erreichbar")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
