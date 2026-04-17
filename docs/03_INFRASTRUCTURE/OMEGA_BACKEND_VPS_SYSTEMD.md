# Omega-Backend auf dem VPS (systemd)

**Vektor:** 2210 | **Delta:** 0.049
**Status:** OPERATIV (Phase 1)
**Übergeordnet:** `OMEGA_BACKEND_VPS_EXECUTION_MASTER_2026-04-04.md`, `OMEGA_DETAILFLUSS_TICKETS_4_12_PROD_RUNTIME.md`, `VPS_HOST_PORT_CONTRACT.md`

---

## 1. Zweck

Gleiche FastAPI-App wie lokal (`src.api.main:app`), betrieben auf dem **VPS** unter **systemd**, mit messbarem Health-Endpunkt `GET /status`.

---

## 2. Pfade und Port

| Größe | Wert |
|--------|------|
| Code auf dem VPS | `/opt/omega-backend` |
| venv | `/opt/omega-backend/.venv` |
| Unit (Repo) | `infra/vps/systemd/omega-backend.service` |
| Environment-Vorlage (Repo) | `infra/vps/systemd/omega-backend.env.template` → auf dem VPS nach `/etc/default/omega-backend` |
| **Host-Port (Vertrag)** | **32800** — Konstante `OMEGA_BACKEND_HOST_PORT` in `src/config/vps_public_ports.py` |

**Bind-Variante (Phase 1):** uvicorn lauscht **direkt** auf `0.0.0.0:32800` (kein Docker-Publish). Die Unit startet per `/bin/bash -lc 'exec …/.venv/bin/python -m uvicorn …'` (wie Anti-Heroin-Service), damit `systemd-analyze verify` auf dem Dev-Host nicht am fehlenden `/opt/omega-backend/.venv/bin/python` scheitert.

---

## 3. Deploy

Vom Rechner mit SSH-Zugang (`VPS_HOST`, optional `VPS_SSH_KEY` in `.env`):

```bash
cd /OMEGA_CORE
.venv/bin/python -m src.scripts.vps_deploy_omega_backend
```

- **Weg:** rsync von `src/` und `requirements.txt` (kein `git pull` auf dem VPS in diesem Skript).
- Setzt `/etc/default/omega-backend` aus der **Template-Datei** (nur Platzhalterkommentare im Repo — **keine Secrets committen**).
- End-to-End-Health per SSH: `curl -sf http://127.0.0.1:32800/status`. Überspringen: `OMEGA_DEPLOY_SKIP_HEALTH=1` (nur wenn bewusst, z. B. fehlende Keys).

---

## 4. Verifikation

- **Loopback auf dem VPS (Upstream, unabhängig von Kong):** `python -m src.scripts.verify_vps_omega_backend_http` — SSH als `root@VPS_HOST`, Remote **`bash -lc`** mit **`set -o pipefail`** und `curl -sf` gegen **`127.0.0.1:<OMEGA_BACKEND_HOST_PORT>/status`** (ohne `pipefail` wäre die Abnahme **falsch grün**, wenn `curl` scheitert und `head` als letztes in der Pipeline Exit 0 liefert). Das ist **nicht** dieselbe Prüfung wie `verify_vps_stack` „Kong Proxy /status“ (Client → Host-Port **32776**; Timeout heißt oft: **von der Kong-Netzwerk-Namespace aus** ist **`172.17.0.1:32800`** nicht erreichbar — z. B. Dienst nur auf `127.0.0.1` gebunden, oder Dienst down).
- **Prod-Abnahme über dieselbe öffentliche Basis wie FastAPI:** In `run_vollkreis_abnahme.py` **`CORE_BASE_URL`** = Schema+Host (+ optional Port), **ohne** trailing slash und **ohne** `/status` — das Skript hängt **`/status`** an. Block **A** und Block **G** (Agent-Pool) nutzen dieselbe Variable.
- Lokale Unit-Syntax: `systemd-analyze verify infra/vps/systemd/omega-backend.service`

---

## 5. Rollback

```bash
ssh root@$VPS_HOST -- systemctl stop omega-backend && systemctl disable omega-backend
```

Optional: rsync-Stand unter `/opt/omega-backend` durch vorheriges Backup ersetzen (Operator-Disziplin).

---

## 6. Kong / öffentlicher Ingress

Später (Phase 2): Proxy-Route z. B. auf `http://127.0.0.1:32800` — **nicht** mit dieser Unit vermischen; siehe Execution-Master §1 und Verkehrsplan.

---

## 7. Chroma-Ingest (Playbook-Dokumente)

Wiederholbar, nur die drei VPS-Playbook-Dateien (Multi-View, Collection `core_vps_playbook`):

```bash
python -m src.scripts.ingest_vps_playbook_chunks
```

Erfordert **laufende, erreichbare** Chroma-Instanz (`CHROMA_HOST` / `CHROMA_PORT` oder lokaler Pfad). Bei Verbindungsfehler: **Exit 1** (kein Fake-Erfolg).

---

[PASS] Betrieb, Ports, Deploy-Skript, Rollback und Verifikation beschrieben.
