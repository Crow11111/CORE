# Ollama-Provider in den RICHTIGEN Pfad schreiben
import paramiko, os, json, base64
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("VPS_HOST", "").strip()
KEY = os.getenv("VPS_SSH_KEY", "").strip().strip('"')
PWD = os.getenv("VPS_PASSWORD", "").strip().strip('"')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
if KEY and os.path.isfile(KEY):
    ssh.connect(HOST, port=22, username="root", key_filename=KEY, timeout=15)
else:
    ssh.connect(HOST, port=22, username="root", password=PWD, timeout=15)
print("[OK] SSH")

def run(cmd, timeout=30):
    i, o, e = ssh.exec_command(cmd, timeout=timeout)
    code = o.channel.recv_exit_status()
    return code, o.read().decode("utf-8", "replace").strip(), e.read().decode("utf-8", "replace").strip()

OLLAMA_PROVIDER = {
    "baseUrl": "http://127.0.0.1:11434",
    "models": [
        {"id": "qwen2.5:7b", "name": "Qwen 2.5 7B (lokal)"},
    ]
}

# RICHTIGER Pfad (wo Container wirklich mountet)
CORRECT_PATHS = [
    "/opt/atlas-core/openclaw-admin/data/openclaw.json",
    "/opt/atlas-core/openclaw-spine/data/openclaw.json",
]

for cfg_path in CORRECT_PATHS:
    print(f"\n--- {cfg_path} ---")
    c, raw, _ = run(f"cat {cfg_path} 2>/dev/null")
    if not raw:
        print("  [SKIP] Nicht vorhanden")
        continue
    
    try:
        cfg = json.loads(raw)
    except:
        print("  [FAIL] Kein JSON")
        continue
    
    # Ollama-Provider hinzufuegen
    if "models" not in cfg:
        cfg["models"] = {}
    if "providers" not in cfg["models"]:
        cfg["models"]["providers"] = {}
    
    cfg["models"]["providers"]["ollama"] = OLLAMA_PROVIDER
    
    # agents.defaults.models
    if "agents" not in cfg:
        cfg["agents"] = {}
    if "defaults" not in cfg["agents"]:
        cfg["agents"]["defaults"] = {}
    if "models" not in cfg["agents"]["defaults"]:
        cfg["agents"]["defaults"]["models"] = {}
    
    cfg["agents"]["defaults"]["models"]["ollama/qwen2.5:7b"] = {"alias": "Qwen 2.5 7B (lokal)"}
    
    # Schreiben
    merged = json.dumps(cfg, indent=2, ensure_ascii=False)
    b64 = base64.standard_b64encode(merged.encode("utf-8")).decode("ascii")
    c, _, err = run(f"echo '{b64}' | base64 -d > {cfg_path}")
    print(f"  [{'OK' if c == 0 else 'FAIL'}] Geschrieben")

# Container neustarten
print("\n--- Container neustarten ---")
for container in ["openclaw-admin", "openclaw-spine"]:
    c, out, _ = run(f"docker restart {container}")
    print(f"  {container}: {'OK' if c == 0 else 'FAIL'}")

import time
print("\nWarte 5 Sekunden...")
time.sleep(5)

# Verifikation
print("\n--- Verifikation: Ollama im Container? ---")
c, out, _ = run("docker exec openclaw-admin cat /home/node/.openclaw/openclaw.json 2>/dev/null | grep -i ollama | head -3")
if "ollama" in out.lower():
    print("  [OK] Ollama-Provider gefunden:")
    print(" ", out)
else:
    print("  [FAIL] Ollama NICHT gefunden")

ssh.close()
print("\n=== FERTIG ===")
