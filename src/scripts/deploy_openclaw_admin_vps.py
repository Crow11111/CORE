"""
Deploy OpenClaw Admin VPS (187.77.68.250).
Setzt Docker, Docker-Compose und Nginx-Proxy für OpenClaw auf.
Nutzt lokale .env Secrets für die Remote-Konfiguration.
"""
import os
import time
from dotenv import load_dotenv
import paramiko
from io import StringIO

# Lade lokale Environment-Variablen
load_dotenv("c:/ATLAS_CORE/.env")
# Lade Secrets (falls nötig, hierarchisch)
load_dotenv("c:/ATLAS_CORE/.secrets.mth", override=True)

VPS_HOST = os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST")
VPS_USER = os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER", "root")
VPS_PASSWORD = os.getenv("OPENCLAW_ADMIN_VPS_PASSWORD") or os.getenv("VPS_PASSWORD")
VPS_SSH_KEY = os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY")

# OpenClaw Config
OC_PORT = os.getenv("OPENCLAW_GATEWAY_PORT", "18789")
OC_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "change_me_token")
WHATSAPP_TARGET = os.getenv("WHATSAPP_TARGET_ID", "")

# Google AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Pfade auf dem VPS
REMOTE_DIR = "/opt/atlas-core/openclaw-admin"
DATA_DIR = f"{REMOTE_DIR}/data"

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Verbinde zu {VPS_USER}@{VPS_HOST}...")
    
    if VPS_SSH_KEY and os.path.exists(VPS_SSH_KEY):
        k = paramiko.Ed25519Key.from_private_key_file(VPS_SSH_KEY)
        client.connect(VPS_HOST, username=VPS_USER, pkey=k)
    elif VPS_PASSWORD:
        client.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)
    else:
        raise ValueError("Keine SSH-Credentials (Passwort oder Key) gefunden.")
    
    return client

def run_command(client, command):
    print(f"EXEC: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    if exit_status != 0:
        print(f"ERROR ({exit_status}): {err}")
        return False, err
    if out:
        print(f"OUT: {out}")
    return True, out

def deploy():
    if not VPS_HOST:
        print("FEHLER: Kein VPS_HOST in .env definiert.")
        return

    ssh = get_ssh_client()
    
    # 1. Basis-Setup (Docker)
    print("\n--- 1. System-Check ---")
    ok, _ = run_command(ssh, "docker --version")
    if not ok:
        print("Installiere Docker...")
        run_command(ssh, "curl -fsSL https://get.docker.com | sh")
    
    # 2. Verzeichnisse
    print("\n--- 2. Verzeichnisse ---")
    run_command(ssh, f"mkdir -p {DATA_DIR}/workspace/rat_submissions")
    run_command(ssh, f"mkdir -p {DATA_DIR}/config")
    
    # 3. Docker Compose File
    print("\n--- 3. Docker Compose ---")
    docker_compose_content = f"""
version: '3.8'

services:
  openclaw:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: openclaw-admin
    restart: unless-stopped
    ports:
      - "{OC_PORT}:8080"
    environment:
      - OPENCLAW_API_TOKEN={OC_TOKEN}
      - GOOGLE_API_KEY={GEMINI_API_KEY}
      - ANTHROPIC_API_KEY={ANTHROPIC_API_KEY}
      - LOG_LEVEL=info
      # WhatsApp Configuration (via Environment oder Config-File)
      # Hier minimalistisch, Rest über Config-File im Volume
    volumes:
      - ./data/config:/app/config
      - ./data/workspace:/app/workspace
    networks:
      - openclaw_net

networks:
    openclaw_net:
        driver: bridge
"""
    # Upload docker-compose.yml
    sftp = ssh.open_sftp()
    with StringIO(docker_compose_content) as f:
        sftp.putfo(f, f"{REMOTE_DIR}/docker-compose.yml")
    print("docker-compose.yml hochgeladen.")
    
    # 4. OpenClaw Config (openclaw.json) - Basis
    # Hier könnte man eine komplexe Config generieren. Fürs erste reicht eine leere/minimale, 
    # da OpenClaw vieles über ENV oder Defaults macht.
    # WICHTIG: Wir müssen sicherstellen, dass WhatsApp aktiviert ist.
    openclaw_config = """
{
  "agents": {
    "main": {
      "name": "ATLAS Admin",
      "model": "gemini-3.1-pro-preview",
      "system_prompt": "Du bist der OpenClaw Admin für ATLAS.",
      "tools": ["whatsapp"]
    }
  },
  "tools": {
    "whatsapp": {
      "enabled": true
    }
  }
}
"""
    with StringIO(openclaw_config) as f:
        sftp.putfo(f, f"{DATA_DIR}/config/openclaw.json")
    print("openclaw.json hochgeladen.")
    sftp.close()

    # 5. Starten
    print("\n--- 4. Starten ---")
    run_command(ssh, f"cd {REMOTE_DIR} && docker compose up -d")
    
    print("\n✅ Deployment abgeschlossen.")
    print(f"OpenClaw sollte unter http://{VPS_HOST}:{OC_PORT} erreichbar sein.")
    print(f"Token: {OC_TOKEN}")

    ssh.close()

if __name__ == "__main__":
    deploy()
