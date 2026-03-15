# Diagnose: Was ist der ECHTE Zustand auf dem VPS?
# Keine Annahmen, nur Fakten.
from __future__ import annotations
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

load_dotenv()
HOST = (os.getenv("VPS_HOST") or "").strip()
USER = (os.getenv("VPS_USER") or "root").strip()
PWD = (os.getenv("VPS_PASSWORD") or "").strip().strip('"')
KEY = (os.getenv("VPS_SSH_KEY") or "").strip().strip('"')
PORT = int(os.getenv("VPS_SSH_PORT") or "22")


def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", "replace").strip()
    err = (stderr.read() or b"").decode("utf-8", "replace").strip()
    return code, out, err


def main():
    print("=" * 60)
    print("DIAGNOSE: Echter Zustand auf VPS", HOST)
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY and os.path.isfile(KEY):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PWD, timeout=15)
        print("[OK] SSH-Verbindung hergestellt\n")
    except Exception as e:
        print(f"[FAIL] SSH-Fehler: {e}")
        return 1

    # 1. Docker Container
    print("--- 1. Docker Container ---")
    c, out, _ = run(ssh, "docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'")
    if out:
        for line in out.splitlines():
            print("  ", line)
    else:
        print("  KEINE CONTAINER")

    # 2. Ollama installiert?
    print("\n--- 2. Ollama Installation ---")
    c, out, err = run(ssh, "which ollama 2>/dev/null && ollama --version 2>&1 || echo 'NICHT_INSTALLIERT'")
    print(" ", out or err or "UNBEKANNT")

    # 3. Ollama Prozess
    print("\n--- 3. Ollama Prozess ---")
    c, out, _ = run(ssh, "pgrep -a ollama 2>/dev/null || echo 'KEIN_PROZESS'")
    print(" ", out)

    # 4. Ollama API
    print("\n--- 4. Ollama API (Port 11434) ---")
    c, out, err = run(ssh, "curl -s --connect-timeout 5 http://127.0.0.1:11434/api/tags 2>&1 || echo 'KEINE_ANTWORT'")
    if "models" in out:
        try:
            data = json.loads(out)
            models = [m.get("name") for m in data.get("models", [])]
            print("  Modelle:", models if models else "KEINE")
        except:
            print(" ", out[:300])
    else:
        print(" ", out[:200] or err[:200] or "KEINE_ANTWORT")

    # 5. OpenClaw Config - Providers
    print("\n--- 5. OpenClaw Config (Admin-Container) ---")
    c, raw, _ = run(ssh, "docker exec openclaw-admin cat /home/node/.openclaw/openclaw.json 2>/dev/null || echo 'NICHT_LESBAR'")
    if raw and raw != "NICHT_LESBAR":
        try:
            cfg = json.loads(raw)
            providers = (cfg.get("models") or {}).get("providers") or {}
            print("  Providers gefunden:", list(providers.keys()) if providers else "KEINE")
            if "ollama" in providers:
                print("  Ollama-Config:", json.dumps(providers["ollama"], indent=2)[:300])
            else:
                print("  [!] KEIN Ollama-Provider in Config!")
            # controlUi
            ctrl = (cfg.get("gateway") or {}).get("controlUi") or {}
            print("  controlUi:", ctrl if ctrl else "NICHT_GESETZT")
        except json.JSONDecodeError:
            print("  Config ist kein valides JSON")
    else:
        print(" ", raw)

    # 6. OpenClaw Logs (letzte 20 Zeilen)
    print("\n--- 6. OpenClaw Admin Logs (letzte 15 Zeilen) ---")
    c, out, _ = run(ssh, "docker logs openclaw-admin --tail 15 2>&1")
    for line in (out or "KEINE_LOGS").splitlines():
        print(" ", line[:120])

    # 7. Port 18789 erreichbar?
    print("\n--- 7. Port 18789 (Gateway) ---")
    c, out, _ = run(ssh, "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:18789/ 2>&1 || echo 'NICHT_ERREICHBAR'")
    print("  HTTP Status:", out)

    ssh.close()
    print("\n" + "=" * 60)
    print("DIAGNOSE ABGESCHLOSSEN")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
