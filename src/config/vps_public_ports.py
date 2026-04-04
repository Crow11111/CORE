# -*- coding: utf-8 -*-
"""
VPS: veröffentlichte Host-Ports — **VERTRAG** (Single Source of Truth).

Diese Zahlen sind die **Soll-Bindung** für Docker-Publish auf dem VPS
(``host:container``). Ein Deploy, der andere Host-Ports auswirft, ist **fehlerhaft**,
bis der Vertrag hier und in der Doku **gemeinsam** geändert wird.

**Pflegepflicht:** Agenten / Producer / Infra — **nicht** der Operator manuell.
Siehe ``docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md``.
"""
from __future__ import annotations

# —— Chroma 1.0.15 (Stack chroma-uvmy, Container chromadb) ——
CHROMA_UVMY_HOST_PORT: int = 32779
CHROMA_UVMY_CONTAINER_PORT: int = 8000

# —— Kong (Stack kong-s7rk) ——
KONG_PROXY_HOST_PORT: int = 32776
KONG_ADMIN_API_HOST_PORT: int = 32777
KONG_MANAGER_UI_HOST_PORT: int = 32778
# Öffentlicher Proxy-Health (request-termination, kein Upstream-Traffic)
KONG_PUBLIC_HEALTH_PATH: str = "/health"
KONG_PUBLIC_HEALTH_BODY: str = "OMEGA_KONG_HEALTH_OK"

# —— Evolution API ——
EVOLUTION_API_HOST_PORT: int = 55775
EVOLUTION_API_CONTAINER_PORT: int = 8080

# —— OpenClaw (kanonisch, ghcr.io/openclaw) ——
OPENCLAW_ADMIN_HOST_PORT: int = 18789
OPENCLAW_SPINE_HOST_PORT: int = 18790

# —— MCP (Cursor / Tooling) ——
MCP_SERVER_HOST_PORT: int = 8001

# —— Monica ——
MONICA_HTTP_HOST_PORT: int = 32772

# —— Home Assistant (ha-atlas auf VPS) ——
HA_ATLAS_HOST_PORT: int = 18123

# —— atlas_agi_core ——
ATLAS_AGI_CORE_HOST_PORT: int = 8080

# —— Hostinger One-Click OpenClaw (parallel; Architektur: auf eine Instanz fokussieren) ——
OPENCLAW_HOSTINGER_HVPS_HOST_PORT: int = 58105
OPENCLAW_HOSTINGER_WSLC_HOST_PORT: int = 55800


def contract_summary() -> str:
    """Eine Zeile pro Port für Logs und Abnahme-Text."""
    pairs = (
        ("CHROMA_UVMY", CHROMA_UVMY_HOST_PORT),
        ("KONG_PROXY", KONG_PROXY_HOST_PORT),
        ("KONG_ADMIN", KONG_ADMIN_API_HOST_PORT),
        ("EVOLUTION_API", EVOLUTION_API_HOST_PORT),
        ("OPENCLAW_ADMIN", OPENCLAW_ADMIN_HOST_PORT),
        ("MCP_SERVER", MCP_SERVER_HOST_PORT),
        ("MONICA", MONICA_HTTP_HOST_PORT),
        ("HA_ATLAS", HA_ATLAS_HOST_PORT),
    )
    return "; ".join(f"{k}={v}" for k, v in pairs)
