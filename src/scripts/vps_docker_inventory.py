import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

import paramiko
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("VPS_HOST")
user = os.getenv("VPS_USER")
password = os.getenv("VPS_PASSWORD")
key_path = os.getenv("VPS_SSH_KEY")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    if key_path and os.path.exists(key_path):
        ssh.connect(host, username=user, key_filename=key_path, timeout=15)
    else:
        ssh.connect(host, username=user, password=password, timeout=15)
    print(f"[OK] Verbunden mit {host}")
except Exception as e:
    print(f"[FAIL] SSH-Verbindung: {e}")
    sys.exit(1)

commands = [
    ("Docker Container (alle)", "docker ps -a --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"),
    ("Docker Images", "docker images --format 'table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}'"),
    ("Docker Volumes", "docker volume ls --format 'table {{.Name}}\\t{{.Driver}}'"),
    ("Docker Networks", "docker network ls --format 'table {{.Name}}\\t{{.Driver}}\\t{{.Scope}}'"),
    ("Docker Compose Projekte (falls vorhanden)", "find /opt -name 'docker-compose*.yml' -o -name 'compose*.yml' 2>/dev/null | head -20"),
    ("Listening Ports", "ss -tlnp | grep -v '127.0.0.53'"),
    ("Ollama Status", "systemctl is-active ollama 2>/dev/null; ollama list 2>/dev/null || echo 'Ollama nicht installiert/aktiv'"),
    ("Disk Usage", "df -h / | tail -1"),
    ("Memory", "free -h | head -2"),
]

for label, cmd in commands:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    _, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if out:
        print(out)
    if err and not out:
        print(f"  (stderr) {err}")
    if not out and not err:
        print("  (keine Ausgabe)")

ssh.close()
print("\n[DONE] VPS Docker Inventory abgeschlossen.")
