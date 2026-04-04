# VPS — Compose-Pfade (Ist, messbar)

**Plan:** `docs/02_ARCHITECTURE/KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` **§8.2** — Deploy: Host-Ports im YAML vernageln; **§8.5** — bei Infra-Change Snapshot (`docker ps`) im Verkehrsplan aktualisieren.

Quelle: `docker inspect …` → `com.docker.compose.project.config_files` / `working_dir` (laufende Container).

| Stack / Dienst | `config_files` (auf dem VPS) | `working_dir` |
|----------------|------------------------------|---------------|
| Kong (`kong-s7rk`) | `/docker/kong-s7rk/docker-compose.yml` | `/docker/kong-s7rk` |
| Chroma 1.0.15 (`chroma-uvmy`) | `/docker/chroma-uvmy/docker-compose.yml` | `/docker/chroma-uvmy` |
| Evolution API (`evolution-api-yxa5`) | `/docker/evolution-api-yxa5/docker-compose.yml` | `/docker/evolution-api-yxa5` |
| MCP-Server | `/opt/atlas-core/mcp-server/docker-compose.yml` | `/opt/atlas-core/mcp-server` |
| `openclaw-admin` | *(kein Compose-Label auf dem gemessenen Container — Startpfad separat klären)* | — |

**Host-Ports:** verbindlich `docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md` und `src/config/vps_public_ports.py`.

**Kong-Deklaration im Repo:** `infra/vps/kong/kong-deck-reference.yaml`.
