---
name: expertise-networking
description: Fachgebiet Netzwerk und API-Design für Schicht-3-Produzenten. Docker, REST/WebSocket, MQTT, SSH-Tunnel. CORE VPS, Scout, Dreadnought, OpenClaw.
---

# Expertise: Netzwerk & API

## Technologie-Stack

| Protokoll | Einsatz |
|-----------|---------|
| REST | API-Endpoints, Webhooks |
| WebSocket | Echtzeit, Core-Events |
| MQTT | IoT, Home Assistant |
| SSH-Tunnel | Sichere Verbindungen |

## Docker-Networking

- Bridge-Netzwerke für Service-Isolation
- Port-Mapping: Host:Container
- Volumes für persistente Daten

## CORE Topologie

| Knoten | Rolle |
|--------|-------|
| VPS (Hostinger) | Zentraler Server, OpenClaw |
| Scout (Raspi) | Edge, Sensoren, HA |
| Dreadnought (Win11) | Dev, Core Omni Node |

## CORE-spezifisch

- **OpenClaw Gateway**: Port 18789
- **API-Design**: RESTful, konsistente Fehlerantworten
- **Webhooks**: HA, WhatsApp, Core-Events
- **SSH-Tunnel**: VPS ↔ Scout/Dreadnought für sichere Kanäle
