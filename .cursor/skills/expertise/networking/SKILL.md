---
name: expertise-networking
description: Fachgebiet Netzwerk und API-Design für Schicht-3-Produzenten. Docker, REST/WebSocket, MQTT, SSH-Tunnel. ATLAS VPS, Scout, Dreadnought, OpenClaw.
---

# Expertise: Netzwerk & API

## Technologie-Stack

| Protokoll | Einsatz |
|-----------|---------|
| REST | API-Endpoints, Webhooks |
| WebSocket | Echtzeit, Atlas-Events |
| MQTT | IoT, Home Assistant |
| SSH-Tunnel | Sichere Verbindungen |

## Docker-Networking

- Bridge-Netzwerke für Service-Isolation
- Port-Mapping: Host:Container
- Volumes für persistente Daten

## ATLAS Topologie

| Knoten | Rolle |
|--------|-------|
| VPS (Hostinger) | Zentraler Server, OpenClaw |
| Scout (Raspi) | Edge, Sensoren, HA |
| Dreadnought (Win11) | Dev, Atlas Omni Node |

## ATLAS-spezifisch

- **OpenClaw Gateway**: Port 18789
- **API-Design**: RESTful, konsistente Fehlerantworten
- **Webhooks**: HA, WhatsApp, Atlas-Events
- **SSH-Tunnel**: VPS ↔ Scout/Dreadnought für sichere Kanäle
