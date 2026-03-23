# Fix: Device-Auth loeschen + Ollama auf Host-IP statt localhost
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
print("[OK] SSH\n")

def run(cmd, timeout=30):
    i, o, e = ssh.exec_command(cmd, timeout=timeout)
    code = o.channel.recv_exit_status()
    return code, o.read().decode("utf-8", "replace").strip(), e.read().decode("utf-8", "replace").strip()

# 1. Host-IP fuer Docker (nicht localhost, sondern docker0 oder host.docker.internal)
print("=== 1. Docker Host-IP ermitteln ===")
c, docker_ip, _ = run("ip -4 addr show docker0 2>/dev/null | grep inet | awk '{print $2}' | cut -d/ -f1")
if not docker_ip:
    # Fallback: Host-IP
    docker_ip = "172.17.0.1"  # Standard Docker Bridge
print(f"  Docker Host-IP: {docker_ip}")

# Teste ob Ollama von dort erreichbar ist
c, out, _ = run(f"curl -s --connect-timeout 3 http://{docker_ip}:11434/api/tags 2>&1")
if "models" in out:
    print(f"  [OK] Ollama erreichbar unter {docker_ip}:11434")
else:
    print(f"  [!] Ollama NICHT erreichbar unter {docker_ip}:11434")
    # Versuche Host-Netzwerk-IP
    c, host_ip, _ = run("hostname -I | awk '{print $1}'")
    docker_ip = host_ip.strip() or "187.77.68.250"
    print(f"  Versuche Host-IP: {docker_ip}")

# 2. Device-Auth loeschen
print("\n=== 2. Device-Auth entfernen ===")
for container in ["openclaw-admin", "openclaw-spine"]:
    c, out, _ = run(f"docker exec {container} rm -f /home/node/.openclaw/identity/device-auth.json 2>&1")
    print(f"  {container}: device-auth.json geloescht")

# 3. Config: Ollama baseUrl auf Host-IP aendern
print("\n=== 3. Ollama baseUrl auf Host-IP aendern ===")
CORRECT_PATH = "/opt/atlas-core/openclaw-admin/data/openclaw.json"
c, raw, _ = run(f"cat {CORRECT_PATH}")
if raw:
    cfg = json.loads(raw)
    if "models" in cfg and "providers" in cfg["models"] and "ollama" in cfg["models"]["providers"]:
        cfg["models"]["providers"]["ollama"]["baseUrl"] = f"http://{docker_ip}:11434"
        print(f"  Ollama baseUrl: http://{docker_ip}:11434")
        
        merged = json.dumps(cfg, indent=2, ensure_ascii=False)
        b64 = base64.standard_b64encode(merged.encode("utf-8")).decode("ascii")
        run(f"echo '{b64}' | base64 -d > {CORRECT_PATH}")
        print("  [OK] Config geschrieben")

# 4. Container neustarten
print("\n=== 4. Container neustarten ===")
for container in ["openclaw-admin", "openclaw-spine"]:
    run(f"docker restart {container}")
    print(f"  {container}: neugestartet")

import time
print("\nWarte 8 Sekunden...")
time.sleep(8)

# 5. Verifikation
print("\n=== 5. Verifikation ===")
c, out, _ = run("docker logs openclaw-admin --tail 20 2>&1 | grep -iE 'ollama|device|identity|error' | tail -10")
print(out if out else "Keine relevanten Logs")

ssh.close()
print("\n=== FERTIG - Browser neu laden! ===")
