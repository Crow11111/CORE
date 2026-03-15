# OpenClaw-Container mit Host-Netzwerk neu erstellen
import paramiko, os, time
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("VPS_HOST", "").strip()
KEY = os.getenv("VPS_SSH_KEY", "").strip().strip('"')
PWD = os.getenv("VPS_PASSWORD", "").strip().strip('"')
TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "").strip().strip('"')

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
    out = o.read().decode("utf-8", "replace").strip()
    err = e.read().decode("utf-8", "replace").strip()
    return code, out, err

# 1. Aktuellen Container stoppen
print("=== 1. Alten Container stoppen ===")
run("docker stop openclaw-admin 2>/dev/null")
run("docker rm openclaw-admin 2>/dev/null")
print("  openclaw-admin gestoppt und entfernt")

# 2. Mit Host-Netzwerk neu starten
print("\n=== 2. Container mit --network host starten ===")
DATA_PATH = "/opt/atlas-core/openclaw-admin/data"

cmd = f"""docker run -d \\
  --name openclaw-admin \\
  --restart unless-stopped \\
  --network host \\
  -v {DATA_PATH}:/home/node/.openclaw \\
  -e HOME=/home/node \\
  -e OPENCLAW_GATEWAY_TOKEN='{TOKEN}' \\
  ghcr.io/openclaw/openclaw:main \\
  node openclaw.mjs gateway --allow-unconfigured --bind lan --port 18789
"""

c, out, err = run(cmd)
if c == 0:
    print("  [OK] Container gestartet")
else:
    print(f"  [FAIL] {err[:300]}")
    
print("\nWarte 5 Sekunden...")
time.sleep(5)

# 3. Container laeuft?
print("\n=== 3. Container-Status ===")
c, out, _ = run("docker ps --filter name=openclaw-admin --format '{{.Names}} {{.Status}}'")
print(f"  {out}")

# 4. Ollama aus Container testen
print("\n=== 4. Ollama-Test aus Container ===")
c, out, _ = run("docker exec openclaw-admin curl -s --connect-timeout 5 http://127.0.0.1:11434/api/tags 2>&1")
if "models" in out:
    print("  [OK] Ollama erreichbar unter 127.0.0.1:11434")
else:
    print(f"  [!] {out[:200]}")

# 5. Logs
print("\n=== 5. Container-Logs ===")
c, out, _ = run("docker logs openclaw-admin --tail 10 2>&1")
print(out[:800])

ssh.close()
print("\n=== FERTIG - Browser testen! ===")
