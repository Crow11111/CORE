# Ausführungsmaster: Omega-Backend als Dienst auf dem VPS

**Status:** OPERATOR-AUFTRAG | **Delta:** 0.049
**Übergeordnet:** `MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md`, `OMEGA_DETAILFLUSS_TICKETS_4_12_PROD_RUNTIME.md`
**Ziel:** FastAPI-Runtime (**gleiche App** wie Dreadnought) auf dem **VPS** unter systemd, **messbar** (Health, Port-Vertrag, Deploy-Skript, pytest), nicht nur `src/`-Scan.

---

## 0. Systemstand (Abfrage 2026-04-04)

| Kanal | Ergebnis |
|-------|----------|
| **MCP `read_core_state`** | Fehler: kein HTTP auf **localhost:8049** (State-Proxy nicht gestartet) |
| **MCP `update_handbook(infra-vps)`** | Fehler: gleicher Proxy |
| **MCP `record_event`** | **Erfolg** — VPS/SSH-Erkenntnis in **omega_events** persistiert (Zero-Trust `memory_hash`) |
| **MCP `get_episodic_history`** | zuvor leer / ohne relevante VPS-Zeilen |
| **Chroma semantisch** | Kein Treffer in `events` zur VPS-Deploy-Thematik; **core_documents**-Collection in dieser Umgebung nicht vorhanden |

**Warum „seit einer Woche“ wenig in Embeddings?**

1. **Ingest-Pipeline** läuft nicht automatisch bei jedem Doku-Commit (`ingest_core_documents` / Multi-View ist manuell oder Daemon-gesteuert).
2. **Kollektionen** weichen je Umgebung ab; ohne erfolgreichen Ingest keine Abfrage-Treffer.
3. **Operator-Wissen** lag primär in **Markdown**, nicht als Chunks in DB.

**Pflege ab jetzt:** Nach jedem VPS-relevanten Deliverable: **(A)** `record_event` wenn Proxy erreichbar, **(B)** dieses Repo-Dok + **(C)** gezielter Ingest (siehe Producer-Task T3).

---

## 1. Neue Vertragsgröße: Host-Port Omega-Backend (VPS)

**Ist:** `8080` = `atlas_agi_core`, `8001` = MCP — **nicht** doppelt belegen.

**Soll (Vorschlag bis Infra bestätigt):** dedizierter Host-Port **`32800`** → Prozess lauscht intern `8000` (uvicorn), Publish nur auf Loopback oder `0.0.0.0` nach Sicherheits-Soll.

**Pflicht im gleichen Änderungssatz:**

- `docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md` — Zeile + Tabelle
- `src/config/vps_public_ports.py` — Konstante `OMEGA_BACKEND_HOST_PORT: int = 32800`
- `verify_vps_docker_port_contract.py` — optionale Regel, **wenn** Container-Name festliegt (oder **nur** systemd: separater Check in neuem Skript `verify_vps_omega_backend_http.py`)

**Kong (später WP-KONG-CORE):** Route von Proxy zu `http://127.0.0.1:32800` oder Docker-Network — im **Phase-2**-Abschnitt dieses Masters festhalten, nicht im selben Commit vermischen, wenn Kong-Deck noch nicht bereit ist.

---

## 2. Architektur (minimal, systemd, kein Docker-Zwang Phase 1)

| Komponente | Beschreibung |
|------------|----------------|
| **Codepfad auf VPS** | `/opt/omega-backend` (rsync oder `git pull` — **ein** Weg im Skript, dokumentiert) |
| **venv** | `/opt/omega-backend/.venv` — `pip install -r requirements.txt` (oder schlankes `requirements-backend.txt`, falls Producer splittet) |
| **Unit** | `infra/vps/systemd/omega-backend.service` — `User`, `WorkingDirectory`, `EnvironmentFile=/etc/default/omega-backend`, `ExecStart=.../uvicorn ...` |
| **Secrets** | **Nie** ins Repo; nur `/etc/default/omega-backend` aus Operator-Template |
| **Health** | `GET /status` — gleicher Endpunkt wie lokal; Abnahme `curl -sf http://127.0.0.1:32800/status` |

---

## 3. Deliverables (Producer — strikt, mit Abnahme)

| ID | Deliverable | Abnahme |
|----|-------------|---------|
| **T1** | `infra/vps/systemd/omega-backend.service` + `infra/vps/systemd/README.md` ergänzen | `systemd-analyze verify` auf Unit-Datei (lokal) Exit 0 |
| **T2** | `src/scripts/vps_deploy_omega_backend.py` | Ein Lauf: rsync/pull, venv, pip, daemon-reload, enable, start; Endausgabe `[PASS]`; **ein** Remote-String pro SSH wie `_ssh_remote_shell` |
| **T3** | `src/scripts/ingest_vps_playbook_chunks.py` (oder Erweiterung `ingest_core_documents`) | Mindestens 3 Dateien: `VPS_HOST_PORT_CONTRACT.md`, `HANDBOOK_INFRA_VPS_LOCAL_MIRROR.md`, dieses Master-Dok → Upsert in **bestehende** Collection (Name aus `ingest_core_documents` / `chroma_client` — nicht raten, Code lesen) |
| **T4** | `tests/test_vps_deploy_omega_backend_unitfile.py` | pytest: Unit-Datei enthält `ExecStart`, `32800` oder `EnvironmentFile` |
| **T5** | `docs/03_INFRASTRUCTURE/OMEGA_BACKEND_VPS_SYSTEMD.md` | Betrieb, Ports, Rollback, Verweis auf Deploy-Skript |
| **T6** | Inventar + Bibliothek + `KANON_EINSTIEG.md` eine Zeile | Pflicht |

---

## 4. Orchestrierung / Token-Disziplin

- **Ein** Producer-Task mit T1–T6; bei **VETO** oder ausbleibendem Deliverable: Task **abbrechen**, Prompt **kürzen** auf fehlendes Tn, **ohne** Kontext-Wiederholung.
- **O2** nur auf **Unit-Sicherheit** (keine Secrets in Unit) und **Port-Kollision** — nach Producer-Diff.
- **Operator:** Proxy **8049** starten, wenn `read_core_state` / `update_handbook` Pflicht werden (`docs` zu Prozess ergänzen — T5).

---

## 5. Nächster konkreter Schritt

**Jetzt:** Producer-Task starten (siehe Cursor `Task`-Briefing unten im Chat-Log).
**Danach:** Auf Dreadnought `python -m src.scripts.vps_deploy_omega_backend` → `[PASS]` → `CORE_BASE_URL=https://…:32800` oder Tunnel für `run_vollkreis` Block A.

---

*[ORCHESTRATOR_A]* — Messbarkeit vor Narrativ.
