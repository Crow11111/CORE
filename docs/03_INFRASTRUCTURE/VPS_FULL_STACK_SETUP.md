<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# VPS Full-Stack Setup - CORE/SHELL

**Deploy-Skript:** src/scripts/deploy_vps_full_stack.py

---

## Was wird deployed?

| Container | Port | Netzwerk | Funktion |
|---|---|---|---|
| homeassistant | 18123 | atlas_net | Home Assistant Docker; Remote HA nach Scout |
| openclaw-admin | 18789 | atlas-core_atlas_net | OC Gehirn; Ollama (qwen2.5:7b), Claude, WhatsApp |
| openclaw-spine | 18790 | atlas-core_atlas_net | OC Spine; sauberes System, nutzt admin als Gateway |
| evolution-api | 55775 | evolution-api-yxa5_default | WhatsApp Multi-Device API Hub (Evolution API) |
| kong | 32776–32778 | kong-s7rk_default | API Gateway (Proxy 32776, Admin 32777, Manager 32778) — **Vertrag:** `VPS_HOST_PORT_CONTRACT.md` |
| monica | 32772 | monica-0mip_default | Personal CRM / Kontaktverwaltung |
| atlas_agi_core | 8080 | atlas_net | AGI-State Persistenz-Layer |
| atlas_chroma_state | intern | atlas_net | ChromaDB 0.4.24 (Legacy AGI-State) |
| atlas_postgres_state | intern | atlas_net | pgvector/pg15 (AGI-State DB) |
| chroma-uvmy | **32779** | chroma-uvmy_default | ChromaDB 1.0.15 (primaere Vektor-DB) |
| mcp-server | 8001 | bridge | MCP Server fuer Tool-Integration |
| openclaw-wslc (Hostinger) | 55800 / 58105 | openclaw-wslc_default / hvps | Hostinger One-Click OpenClaw — siehe Vertrag |

## Netzwerk-Isolation

| Netzwerk | Typ | Zugriff |
|---|---|---|
| atlas_net | bridge | Internet (Gemini/Anthropic/Nexos-APIs), Kommunikation zwischen Containern |

*(Hinweis: Die alte Aufsplittung in separate openclaw_admin_net, openclaw_spine_net und chroma_net wurde zugunsten eines übersichtlichen `docker-compose` mit `atlas_net` vereinfacht. Eine separate chroma-core Instanz entfällt, da `chroma-uvmy` genutzt wird.)*

## Firewall (ufw)

Offen: 22/tcp, 18789/tcp, 18790/tcp, 18123/tcp, 443/tcp, 80/tcp, 11434/tcp (Ollama), 55775/tcp (Evolution API), 55800/tcp (Hostinger OC).
Geblockt: 8000/tcp (ChromaDB nur intern).
Ollama: systemd-Daemon, bound auf 0.0.0.0:11434, Modell qwen2.5:7b.

---

## Deploy ausfuehren

    # Dry-run (kein SSH, nur Ausgabe):
    python -m src.scripts.deploy_vps_full_stack --dry-run

    # Echtes Deployment:
    python -m src.scripts.deploy_vps_full_stack

    # Ohne HA-Container:
    python -m src.scripts.deploy_vps_full_stack --skip-ha

    # Ohne Extraktion des alten VPS:
    python -m src.scripts.deploy_vps_full_stack --skip-extract

---

## Benoetiate .env-Variablen

    OPENCLAW_ADMIN_VPS_HOST=<IP>
    OPENCLAW_ADMIN_VPS_USER=root
    OPENCLAW_ADMIN_VPS_PASSWORD=...
    GEMINI_API_KEY=...
    ANTHROPIC_API_KEY=...
    NEXOS_API_KEY=...          (optional)
    OPENCLAW_GATEWAY_TOKEN=... (Admin)
    OPENCLAW_SPINE_TOKEN=...   (optional)
    HA_VPS_PORT=18123
    HA_URL=http://192.168.178.54:8123
    HA_TOKEN=eyJ...

---

## Naechste Schritte nach dem Deploy

1. HA Ersteinrichtung: http://<VPS_HOST>:18123
2. HACS installieren: https://hacs.xyz/docs/setup/download
3. Remote Home Assistant: HACS -> Remote Home Assistant -> HA neu starten
4. Scout HA erreichbar machen:
   Option A: Nabu Casa (HA Cloud) -> oeffentliche URL
   Option B: Reverse-SSH-Tunnel von Scout:
             autossh -M 0 -R 18124:localhost:8123 root@<VPS_HOST> -N -f
5. OpenClaw Admin testen: curl http://<VPS_HOST>:18789/api/status
6. OpenClaw Spine befuellen: python -m src.scripts.check_openclaw_config_vps
7. CORE .env ergaenzen:
   OPENCLAW_ADMIN_VPS_HOST=<VPS_HOST>
   OPENCLAW_GATEWAY_PORT=18789
   HA_VPS_URL=http://<VPS_HOST>:18123

---

## Ollama (Strang B)

Lokales LLM auf demselben VPS: siehe **VPS_OLLAMA_SETUP.md**. Installation: `python -m src.scripts.install_ollama_vps`.

---

## Referenzen

- OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md (CORS, Origins, Pfade)
- VPS_OLLAMA_SETUP.md (Ollama Port 11434, Modell, Firewall)
- OPENCLAW_ADMIN_ARCHITEKTUR.md
- PROJEKT_ANNAHMEN_UND_KORREKTUREN.md
- NEXOS_EINBINDUNG.md
- OPENCLAW_GATEWAY_TOKEN.md
