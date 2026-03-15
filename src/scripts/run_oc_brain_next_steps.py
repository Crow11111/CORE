# ============================================================
# CORE-GENESIS: Nächste Schritte wirklich ausführen (keine Simulation)
# - Doctor im Container openclaw-admin
# - Ollama-Daemon starten, api/tags prüfen
# ============================================================
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

load_dotenv()
HOST = (os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST") or "").strip()
USER = (os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER") or "root").strip()
PASSWORD = (os.getenv("OPENCLAW_ADMIN_VPS_PASSWORD") or os.getenv("VPS_PASSWORD") or "").strip().strip('"')
KEY = (os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY") or "").strip().strip('"')
PORT = int(os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or os.getenv("VPS_SSH_PORT", "22"))


def run(ssh: paramiko.SSHClient, cmd: str, timeout_sec: int = 60) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout_sec)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return code, out, err


def main() -> int:
    if not HOST or not USER:
        print("FEHLER: OPENCLAW_ADMIN_VPS_HOST/VPS_HOST und USER in .env fehlen.")
        return 1

    print(f"[SSH] {USER}@{HOST}:{PORT} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY and os.path.isfile(KEY):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)
        print("  Verbindung OK.")
    except Exception as e:
        print(f"  SSH-Fehler: {e}")
        return 1

    try:
        # 1) openclaw doctor im Container openclaw-admin (nicht spine)
        print("\n--- openclaw doctor (openclaw-admin) ---")
        code, out, err = run(ssh, "docker exec openclaw-admin openclaw doctor 2>&1", timeout_sec=45)
        text = out or err or "(keine Ausgabe)"
        print(text[:3000])
        if code != 0:
            print(f"Exit-Code: {code}")
        else:
            print("Doctor: OK")

        # 2) Ollama starten falls nicht läuft, dann api/tags
        print("\n--- Ollama starten + api/tags ---")
        run(ssh, "pgrep -x ollama >/dev/null || (nohup ollama serve >> /var/log/ollama.log 2>&1 &)", timeout_sec=5)
        time.sleep(5)
        code, out, err = run(ssh, "curl -s --connect-timeout 10 http://127.0.0.1:11434/api/tags", timeout_sec=15)
        raw = (out or err or "").strip()
        if code == 0 and raw and ("models" in raw or "error" in raw.lower()):
            print("Ollama api/tags: OK")
            print(raw[:500])
        else:
            print("Ollama api/tags: Fehler oder leer. Ausgabe:", raw[:400] or "(leer)")
            code2, list_out, _ = run(ssh, "ollama list 2>&1; pgrep -x ollama || echo 'ollama-Prozess nicht gefunden'", timeout_sec=10)
            print("ollama list / pgrep:", (list_out or "")[:300])
    finally:
        ssh.close()

    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
