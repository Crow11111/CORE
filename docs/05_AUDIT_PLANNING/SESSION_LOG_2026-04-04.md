# SESSION LOG: 2026-04-04 — VPS Host-Port-Vertrag & Doku-Konsolidierung

**Datum:** 2026-04-04  
**Operator:** Marc  
**Thema:** Verbindliche VPS-Host-Ports (Single Source of Truth), Kanon/Bibliothek/Inventar, Vollkreis-Defaults; Commit/Push ohne `.env`.

## 1. Deliverables (Repo)

| Status | Deliverable | Pfade / Hinweis |
|--------|-------------|-----------------|
| Done | **VPS Host-Port-Vertrag** (Doku) | `docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md` |
| Done | **Code-SSoT öffentliche Ports** (bereits auf `main` vor dieser Session) | `src/config/vps_public_ports.py`; Anbindung in `verify_vps_stack`, Heartbeat, Gravitator, `chroma_client`, `run_vollkreis_abnahme` |
| Done | **Kanon & Bibliothek** | `KANON_EINSTIEG.md`, `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` — Verweis Vertrag + Chroma **32779** |
| Done | **VPS-Infra-Docs** | `VPS_KNOTEN_UND_FLUSSE.md`, `VPS_FULL_STACK_SETUP.md` — an Vertrag angeglichen |
| Done | **Inventar** | `docs/00_STAMMDOKUMENTE/CORE_INVENTORY_REGISTER.md` — Vertrag + `vps_public_ports.py` |
| Done | **Vollkreis** | `run_vollkreis_abnahme.py` — Chroma-Default/Heartbeat konsistent mit Vertrag |

## 2. Operator vs. Technik

- **Operator:** keine manuelle Portliste pflegen; Abnahme: Realität (Compose/Panel/`docker ps`) muss zur Vertragstabelle passen.  
- **Technik/Agenten:** bei jedem Deploy Vertrag, Skripte und ggf. Verkehrsplan-Anhang aktualisieren.

## 3. Verifikation (lokal, diese Session)

- **Anti-Heroin:** `validate_file` auf relevante `.py`-Module (vorherige Runde) — PASS.  
- **Pytest:** `PYTHONPATH=/OMEGA_CORE .venv/bin/python -m pytest tests/test_ticket_10.py -v` — **2 passed** (Infrastructure-Heartbeat / Ticket-10-Verträge).  
- **Gravitator:** dedizierte Testsuite im Repo **fehlt**; Routing/Chroma-Pfad wird indirekt über Integration/Vollkreis abgedeckt — optional Follow-up: Unit-Test für `_discover` mit gemocktem Env.

## 4. Drift / VPS-Hinweis

Host-Ports müssen in **Docker Compose / Hostinger** numerisch fest verdrahtet sein; andernfalls driftet die Laufzeit trotz Vertrag. Repo definiert Soll; Abweichung = bewusste Vertragsänderung + Repo-Nachziehen.

## 5. Agos-Takt-Status

Schnittstellen-Doku als **Arbeitsauftrag für Producer/Auditor**: vor/nach Deploy gegen `VPS_HOST_PORT_CONTRACT.md` und `vps_public_ports.py` prüfen; Operator nur bei strategischer Abweichung eingreifen.
