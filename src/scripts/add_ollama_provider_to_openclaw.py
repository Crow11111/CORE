# Fuegt Ollama-Provider zur OpenClaw-Config hinzu und startet Container neu
from __future__ import annotations
import os
import sys
import json
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

load_dotenv()
HOST = (os.getenv("VPS_HOST") or "").strip()
USER = (os.getenv("VPS_USER") or "root").strip()
PWD = (os.getenv("VPS_PASSWORD") or "").strip().strip('"')
KEY = (os.getenv("VPS_SSH_KEY") or "").strip().strip('"')
PORT = int(os.getenv("VPS_SSH_PORT") or "22")

OLLAMA_PROVIDER = {
    "baseUrl": "http://127.0.0.1:11434",
    "models": [
        {"id": "qwen2.5:7b", "name": "Qwen 2.5 7B (lokal)"},
        {"id": "qwen2.5:14b", "name": "Qwen 2.5 14B (lokal)"},
        {"id": "mistral:7b-instruct", "name": "Mistral 7B Instruct (lokal)"},
    ]
}

CONFIG_PATHS = [
    "/opt/core-core/openclaw-admin/data/openclaw.json",
    "/opt/core-core/openclaw-spine/data/openclaw.json",
]


def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", "replace").strip()
    err = (stderr.read() or b"").decode("utf-8", "replace").strip()
    return code, out, err


def main():
    print("=" * 60)
    print("Ollama-Provider zu OpenClaw hinzufuegen")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY and os.path.isfile(KEY):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PWD, timeout=15)
        print("[OK] SSH-Verbindung\n")
    except Exception as e:
        print(f"[FAIL] SSH: {e}")
        return 1

    for cfg_path in CONFIG_PATHS:
        print(f"--- Bearbeite: {cfg_path} ---")
        
        # Config lesen
        c, raw, _ = run(ssh, f"cat {cfg_path} 2>/dev/null")
        if not raw or c != 0:
            print(f"  [SKIP] Datei nicht lesbar\n")
            continue
        
        try:
            cfg = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"  [FAIL] Kein valides JSON: {e}\n")
            continue
        
        # Provider hinzufuegen
        if "models" not in cfg:
            cfg["models"] = {}
        if "providers" not in cfg["models"]:
            cfg["models"]["providers"] = {}
        
        cfg["models"]["providers"]["ollama"] = OLLAMA_PROVIDER
        print(f"  [+] Ollama-Provider hinzugefuegt")
        
        # In agents.defaults auch Ollama-Modelle registrieren
        if "agents" not in cfg:
            cfg["agents"] = {}
        if "defaults" not in cfg["agents"]:
            cfg["agents"]["defaults"] = {}
        if "models" not in cfg["agents"]["defaults"]:
            cfg["agents"]["defaults"]["models"] = {}
        
        for m in OLLAMA_PROVIDER["models"]:
            key = f"ollama/{m['id']}"
            cfg["agents"]["defaults"]["models"][key] = {"alias": m["name"]}
        print(f"  [+] Modelle in agents.defaults registriert")
        
        # Zurueckschreiben
        merged = json.dumps(cfg, indent=2, ensure_ascii=False)
        b64 = base64.standard_b64encode(merged.encode("utf-8")).decode("ascii")
        
        dir_path = cfg_path.rsplit("/", 1)[0]
        run(ssh, f"mkdir -p {dir_path}")
        c, _, err = run(ssh, f"echo '{b64}' | base64 -d > {cfg_path}")
        if c == 0:
            print(f"  [OK] Config geschrieben")
        else:
            print(f"  [FAIL] Schreiben: {err}")
        print()

    # Container neustarten
    print("--- Container neustarten ---")
    for container in ["openclaw-admin", "openclaw-spine"]:
        c, out, err = run(ssh, f"docker restart {container} 2>&1")
        print(f"  {container}: {out or err}")
    
    # Warten und pruefen
    import time
    print("\nWarte 5 Sekunden...")
    time.sleep(5)
    
    # Verifikation
    print("\n--- Verifikation: Ollama-Provider in Config? ---")
    c, out, _ = run(ssh, "docker exec openclaw-admin cat /home/node/.openclaw/openclaw.json 2>/dev/null | grep -i ollama | head -5")
    if "ollama" in out.lower():
        print("  [OK] Ollama-Provider gefunden:")
        print(" ", out[:200])
    else:
        print("  [FAIL] Ollama-Provider NICHT gefunden")

    ssh.close()
    print("\n" + "=" * 60)
    print("FERTIG - Browser-Test erforderlich!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
