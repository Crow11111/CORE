#!/usr/bin/env python3
"""
VPS-Stack-Verifikation: Container-Status + Chroma v2 Heartbeat.
Siehe docs/BIBLIOTHEK_KERN_DOKUMENTE.md „Wo nachschauen“ und docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md.
"""
import os
import subprocess
import sys
import httpx
from dotenv import load_dotenv
load_dotenv("/OMEGA_CORE/.env")

VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250")
VPS_SSH_KEY = os.getenv("VPS_SSH_KEY", "/home/mth/.ssh/id_ed25519_hostinger")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "32768"))

def run_ssh(cmd: str) -> tuple[int, str]:
    full = f'ssh -o ConnectTimeout=5 -o BatchMode=yes -i "{VPS_SSH_KEY}" root@{VPS_HOST} "{cmd}"'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=15)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def main():
    ok = True
    # 1) Docker ps
    code, out = run_ssh("docker ps --format '{{.Names}} {{.Status}}'")
    if code != 0:
        print("[FAIL] VPS SSH oder docker ps:", out[:400])
        ok = False
    else:
        lines = [l for l in out.strip().split("\n") if l]
        expected = ["openclaw-admin", "chroma-uvmy-chromadb", "mcp-server", "ha-atlas"]
        for name in expected:
            if any(name in l and "Up" in l for l in lines):
                print(f"[OK] {name}")
            else:
                print(f"[WARN] {name} nicht Up oder fehlt")
                ok = False
        print(f"  Container gesamt: {len(lines)}")
    # 2) Chroma v2 heartbeat
    try:
        r = httpx.get(f"http://{VPS_HOST}:{CHROMA_PORT}/api/v2/heartbeat", timeout=5.0)
        if r.status_code == 200 and "heartbeat" in r.text:
            print("[OK] Chroma v2 heartbeat")
        else:
            print("[FAIL] Chroma v2:", r.status_code, r.text[:200])
            ok = False
    except Exception as e:
        print("[FAIL] Chroma v2:", e)
        ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
