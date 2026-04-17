# Handbuch-Spiegel: infra-vps (lokal, wenn MCP-Proxy down)

**Zweck:** `update_handbook(role=infra-vps)` schreibt auf den VPS via **localhost:8049**. Wenn der Sync-Relay nicht läuft, ist dieses File die **kanonische Kopie** bis der Proxy wieder erreichbar ist. Dann Inhalt per MCP nachziehen oder `ingest_core_documents` einbinden.

**Letzte inhaltliche Quelle:** Orchestrator 2026-04-04 (OpenSSH-argv, Anti-Heroin-Deploy, Vertrag).

## OpenSSH + Python subprocess

- Argumente nach `user@host` werden zu **einer** Remote-Command-Zeile verbunden.
- **Falsch:** `['sh', '-c', 'mkdir -p /x && y']` als mehrere argv nach dem Host → bricht; `mkdir: missing operand`.
- **Richtig:** **Ein** Listenelement: vollständige Shell-Zeile. Implementierung: `_ssh_remote_shell` in `src/scripts/vps_deploy_anti_heroin_mirror.py`.

## .env / Cursor

- Deploy-Skripte: `load_dotenv(..., override=True)`, damit eine leere IDE-`VPS_SSH_KEY` nicht `.env` blockiert.

## Anti-Heroin auf VPS

- Spiegel: `/opt/omega-core-mirror/src/` (rsync).
- systemd: `omega-core-anti-heroin.service` + `.timer`.
- Deploy: `python -m src.scripts.vps_deploy_anti_heroin_mirror`.

## Ports

- `VPS_HOST_PORT_CONTRACT.md` + `src/config/vps_public_ports.py`.
- Drift: `verify_vps_stack` + `verify_vps_docker_port_contract`.

## MCP omega-state

- `read_core_state`, `record_event`, `update_handbook` erwarten lokalen Dienst **localhost:8049** (`state_mtls_proxy` o. ä.). Ohne Dienst: Events ggf. nur bei erreichbarem Backend; Handbuch → dieser Spiegel (Fallback-Pfad: diese Datei unter `docs/03_INFRASTRUCTURE/handbooks/`).

**Vollständige Spiegel-Doku:** `docs/03_INFRASTRUCTURE/HANDBOOK_INFRA_VPS_LOCAL_MIRROR.md`
