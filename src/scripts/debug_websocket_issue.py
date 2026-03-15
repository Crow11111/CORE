# Debug: Warum scheitert WebSocket?
import paramiko, os
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
    return o.read().decode("utf-8", "replace").strip()

# 1. Container-Logs mit Filterung auf Fehler
print("=== OpenClaw Admin Logs (error/warning) ===")
logs = run("docker logs openclaw-admin --tail 50 2>&1 | grep -iE 'error|warn|fail|device|identity|auth' | tail -20")
print(logs if logs else "Keine Fehler-Logs gefunden")

# 2. Gesamte letzte Logs
print("\n=== Letzte 30 Zeilen Logs ===")
print(run("docker logs openclaw-admin --tail 30 2>&1"))

# 3. Welche Config-Optionen sind gesetzt?
print("\n=== Gateway-Config ===")
print(run("docker exec openclaw-admin cat /home/node/.openclaw/openclaw.json 2>/dev/null | grep -A30 '\"gateway\"' | head -35"))

# 4. Device-Identity-Verzeichnis
print("\n=== Identity-Verzeichnis ===")
print(run("docker exec openclaw-admin ls -la /home/node/.openclaw/identity/ 2>&1"))

# 5. Credentials-Verzeichnis
print("\n=== Credentials-Verzeichnis ===")
print(run("docker exec openclaw-admin ls -la /home/node/.openclaw/credentials/ 2>&1"))

# 6. OpenClaw Version
print("\n=== OpenClaw Version ===")
print(run("docker exec openclaw-admin openclaw --version 2>&1"))

ssh.close()
