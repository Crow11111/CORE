import os

with open("src/scripts/deploy_vps_full_stack.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_admin = """def step_openclaw_admin(ssh, dry, wa_extracted):
    print(f"\\n[4] OpenClaw Admin (Tabula Rasa) & HA via Docker Compose ...")
    if not OC_ADMIN_TOKEN:
        print("  OPENCLAW_GATEWAY_TOKEN fehlt - uebersprungen.")
        return
        
    # 1. Clone Official Repository
    run(ssh, "test -d /opt/openclaw || git clone https://github.com/openclaw/openclaw.git /opt/openclaw", check=False, dry=dry)
    
    # 2. Set .env for OpenClaw
    env_content = (
        f"OPENCLAW_IMAGE=ghcr.io/openclaw/openclaw:latest\\n"
        f"OPENCLAW_GATEWAY_TOKEN={OC_ADMIN_TOKEN}\\n"
        f"GEMINI_API_KEY={GEMINI_KEY}\\n"
        f"OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=true\\n"
        f"BASE_PATH=/openclaw\\n"
    )
    b64write(ssh, "/opt/openclaw/.env", env_content, dry=dry)

    # 3. Read synced local openclaw.json
    local_cfg_path = os.path.join(os.path.dirname(__file__), "..", "..", "infra", "vps", "openclaw", "openclaw.json")
    if os.path.isfile(local_cfg_path):
        with open(local_cfg_path, "r", encoding="utf-8") as f:
            cfg_content = f.read()
        mkdir(ssh, "/opt/openclaw/data", dry=dry)
        b64write(ssh, "/opt/openclaw/data/openclaw.json", cfg_content, dry=dry)
        run(ssh, "chown -R 1000:1000 /opt/openclaw/data", check=False, dry=dry)
    else:
        print("WARNUNG: Lokale openclaw.json nicht gefunden in infra/vps/openclaw/!")

    # 3b. Read synced tcp-mcp.js
    local_tcp_path = os.path.join(os.path.dirname(__file__), "..", "..", "infra", "vps", "openclaw", "tcp-mcp.js")
    if os.path.isfile(local_tcp_path):
        with open(local_tcp_path, "r", encoding="utf-8") as f:
            tcp_content = f.read()
        b64write(ssh, "/opt/openclaw/tcp-mcp.js", tcp_content, dry=dry)
        run(ssh, "chown 1000:1000 /opt/openclaw/tcp-mcp.js", check=False, dry=dry)

    # 4. Start Container
    run(ssh, "cd /opt/openclaw && docker compose pull && docker compose up -d", check=False, dry=dry)
    import time
    time.sleep(3)

    # 5. Connect to Networks
    run(ssh, "docker network connect atlas_net openclaw-openclaw-gateway-1 2>/dev/null || true", check=False, dry=dry)
    run(ssh, "docker network connect evolution-api-yxa5_default openclaw-openclaw-gateway-1 2>/dev/null || true", check=False, dry=dry)

    # HA Config
    base_ha = "/opt/omega-core/homeassistant"
    mkdir(ssh, f"{base_ha}/config", dry=dry)
    scout_raw = SCOUT_HA_URL.replace("http://","").replace("https://","")
    scout_host = scout_raw.split(":")[0]
    scout_port = scout_raw.split(":")[-1].rstrip("/") if ":" in scout_raw else "8123"
    scout_secure = "true" if SCOUT_HA_URL.startswith("https") else "false"
    config_yaml = (
        "# Home Assistant VPS - Auto-generiert von deploy_vps_full_stack.py\\n\\n"
        "remote_homeassistant:\\n  instances:\\n"
        f"    - host: {scout_host}\\n      port: {scout_port}\\n"
        "      access_token: !secret scout_ha_token\\n"
        f"      secure: {scout_secure}\\n      verify_ssl: false\\n"
        "      filter:\\n        include_domains:\\n"
        "          - light\\n          - switch\\n          - sensor\\n"
        "          - binary_sensor\\n          - automation\\n"
        "          - input_boolean\\n          - media_player\\n"
        "          - camera\\n\\n"
        "logger:\\n  default: warning\\n  logs:\\n"
        "    homeassistant.components.remote_homeassistant: info\\n"
    )
    secrets_yaml = f'scout_ha_token: "{SCOUT_HA_TOKEN}"\\n'

    c, out, _ = run(ssh, f"test -f {base_ha}/config/configuration.yaml && echo exists || echo missing", check=False, dry=dry)
    if dry or "missing" in out:
        b64write(ssh, f"{base_ha}/config/configuration.yaml", config_yaml, dry=dry)
    b64write(ssh, f"{base_ha}/config/secrets.yaml", secrets_yaml, dry=dry)
    run(ssh, f"chmod 600 {base_ha}/config/secrets.yaml", check=False, dry=dry)

    compose_yml = f\"\"\"
version: '3.8'

services:
  ha-core:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: ha-core
    restart: unless-stopped
    environment:
      - TZ=Europe/Berlin
    volumes:
      - ./homeassistant/config:/config
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "{PORT_HA}:8123"
    networks:
      - core_net
    cap_add:
      - NET_ADMIN
      - NET_RAW

networks:
  core_net:
    driver: bridge
\"\"\"
    b64write(ssh, "/opt/omega-core/docker-compose.yml", compose_yml.strip(), dry=dry)
    run(ssh, "cd /opt/omega-core && docker compose pull && docker compose up -d ha-core", check=False, dry=dry)
    time.sleep(5)
    run(ssh, "docker ps --format '{{.Names}}' | grep -iE 'openclaw|ha-core'", check=False, dry=dry)
"""

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith("def step_openclaw_admin"):
        start_idx = i
    elif line.startswith("    time.sleep(5)") and start_idx != -1 and end_idx == -1:
        end_idx = i + 2  # include the next run command

if start_idx != -1 and end_idx != -1:
    lines[start_idx:end_idx] = [new_admin]
    with open("src/scripts/deploy_vps_full_stack.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Patched successfully")
else:
    print(f"Failed to find indices: start={start_idx}, end={end_idx}")

