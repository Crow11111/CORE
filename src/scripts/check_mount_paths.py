# Wo liest der Container seine Config wirklich?
import paramiko, os, json
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

def run(cmd):
    i, o, e = ssh.exec_command(cmd, timeout=30)
    return o.read().decode("utf-8", "replace").strip()

print("=== Container Mount-Info (openclaw-admin) ===")
mounts_raw = run('docker inspect openclaw-admin --format "{{json .Mounts}}"')
try:
    mounts = json.loads(mounts_raw)
    for m in mounts:
        print(f"  {m.get('Source')} -> {m.get('Destination')}")
except:
    print(mounts_raw[:500])

print("\n=== Host-Pfad Config (wo ich geschrieben habe) ===")
print(run("cat /opt/omega-core/openclaw-admin/data/openclaw.json 2>/dev/null | grep -i ollama | head -3") or "NICHT_GEFUNDEN")

print("\n=== Container-Pfad Config (wo Container liest) ===")
print(run("docker exec openclaw-admin cat /home/node/.openclaw/openclaw.json 2>/dev/null | grep -i ollama | head -3") or "NICHT_GEFUNDEN")

print("\n=== Container ls /home/node/.openclaw/ ===")
print(run("docker exec openclaw-admin ls -la /home/node/.openclaw/ 2>&1"))

ssh.close()
