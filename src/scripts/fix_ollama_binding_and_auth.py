# Fix: Ollama auf 0.0.0.0 binden + Auth-Mode auf "none" setzen
import paramiko, os, json, base64, time
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
print("[OK] SSH\n")

def run(cmd, timeout=60):
    i, o, e = ssh.exec_command(cmd, timeout=timeout)
    code = o.channel.recv_exit_status()
    return code, o.read().decode("utf-8", "replace").strip(), e.read().decode("utf-8", "replace").strip()

# 1. Ollama stoppen und mit OLLAMA_HOST=0.0.0.0 neu starten
print("=== 1. Ollama auf 0.0.0.0:11434 binden ===")
run("pkill ollama 2>/dev/null; sleep 2")
run("OLLAMA_HOST=0.0.0.0:11434 nohup ollama serve >> /var/log/ollama.log 2>&1 &")
print("  Ollama neugestartet mit OLLAMA_HOST=0.0.0.0:11434")
time.sleep(3)

# Test
c, out, _ = run("curl -s --connect-timeout 5 http://0.0.0.0:11434/api/tags 2>&1")
if "models" in out:
    print("  [OK] Ollama antwortet auf 0.0.0.0:11434")
else:
    print(f"  [!] Ollama-Test: {out[:100]}")

# 2. OpenClaw Config: Auth komplett deaktivieren (fuer Debugging)
print("\n=== 2. OpenClaw Auth auf 'none' setzen ===")
CORRECT_PATH = "/opt/atlas-core/openclaw-admin/data/openclaw.json"
c, raw, _ = run(f"cat {CORRECT_PATH}")
if raw:
    cfg = json.loads(raw)
    
    # Auth komplett deaktivieren
    if "gateway" not in cfg:
        cfg["gateway"] = {}
    cfg["gateway"]["auth"] = {"mode": "none"}
    cfg["gateway"]["controlUi"] = {
        "allowedOrigins": ["*"],
        "dangerouslyAllowHostHeaderOriginFallback": True,
        "allowInsecureAuth": True,
        "dangerouslyDisableDeviceAuth": True,
        "dangerouslyDisableAuth": True,
    }
    
    # Ollama baseUrl auf localhost (Container sieht jetzt Host-Netzwerk)
    if "models" in cfg and "providers" in cfg["models"] and "ollama" in cfg["models"]["providers"]:
        # Fuer host-network: localhost funktioniert
        cfg["models"]["providers"]["ollama"]["baseUrl"] = "http://host.docker.internal:11434"
    
    merged = json.dumps(cfg, indent=2, ensure_ascii=False)
    b64 = base64.standard_b64encode(merged.encode("utf-8")).decode("ascii")
    run(f"echo '{b64}' | base64 -d > {CORRECT_PATH}")
    print("  [OK] Config mit auth=none geschrieben")

# 3. Identity-Ordner komplett leeren
print("\n=== 3. Identity-Ordner leeren ===")
for container in ["openclaw-admin", "openclaw-spine"]:
    run(f"docker exec {container} rm -rf /home/node/.openclaw/identity/* 2>/dev/null")
    run(f"docker exec {container} rm -rf /home/node/.openclaw/devices/* 2>/dev/null")
    print(f"  {container}: identity + devices geleert")

# 4. Container mit Host-Netzwerk neustarten? Nein, erstmal normal
print("\n=== 4. Container neustarten ===")
for container in ["openclaw-admin", "openclaw-spine"]:
    run(f"docker restart {container}")
    print(f"  {container}: neugestartet")

print("\nWarte 10 Sekunden...")
time.sleep(10)

# 5. Verifikation
print("\n=== 5. Logs pruefen ===")
c, out, _ = run("docker logs openclaw-admin --tail 15 2>&1 | grep -iE 'listen|error|device|auth|ollama' | tail -10")
print(out if out else "Keine relevanten Logs")

# 6. Ollama von Container aus testen
print("\n=== 6. Ollama aus Container testen ===")
c, out, _ = run("docker exec openclaw-admin curl -s --connect-timeout 5 http://host.docker.internal:11434/api/tags 2>&1 || echo 'NICHT_ERREICHBAR'")
print(f"  host.docker.internal: {out[:100] if out else 'leer'}")

c, out, _ = run("docker exec openclaw-admin curl -s --connect-timeout 5 http://172.17.0.1:11434/api/tags 2>&1 || echo 'NICHT_ERREICHBAR'")
print(f"  172.17.0.1: {out[:100] if out else 'leer'}")

ssh.close()
print("\n=== FERTIG ===")
