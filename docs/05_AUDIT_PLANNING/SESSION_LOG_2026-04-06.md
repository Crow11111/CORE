# Session-Log 2026-04-06

**Thema:** Operator-Mandat — Prod ohne Dreadnought als Runtime, MASTER-Work-Pakete, Vollkreis `CORE_BASE_URL`, MACRO-Draft entkanonisiert, VPS Anti-Heroin-Soll, Kanon/Anker/O2-Nachtrag.

## Deliverables

| Status | Artefakt |
|--------|----------|
| done | `docs/05_AUDIT_PLANNING/MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md` |
| done | `docs/03_INFRASTRUCTURE/VPS_ANTI_HEROIN_PIPELINE.md` — systemd + Deploy-Skript |
| done | `src/scripts/run_anti_heroin_scan.py`, `vps_deploy_anti_heroin_mirror.py`, `infra/vps/systemd/*`, `tests/test_run_anti_heroin_scan.py` |
| done | `run_vollkreis_abnahme.py` — `CORE_BASE_URL`, Block A Remote/lokal |
| done | `docs/05_AUDIT_PLANNING/MACRO_CHAIN_MASTER_DRAFT.md` — Operator-Disclaimer |
| done | `docs/00_STAMMDOKUMENTE/OMEGA_RESONANCE_ANCHOR.md` §4 |
| done | `docs/05_AUDIT_PLANNING/O2_AUDIT_KETTEN_KOHAERENZ_2026-04-06.md` §10 + Textkorrekturen |
| done | `KANON_EINSTIEG.md`, `docs/BIBLIOTHEK_KERN_DOKUMENTE.md`, `CORE_INVENTORY_REGISTER.md` |
| done | `ARBEITSPLAN_WORKER_PIPELINE_OFFENE_PUNKTE_2026-04-06.md` — Worker-Pipeline + Backlog |

## Verifikation

- `anti_heroin_validator.validate_file('run_vollkreis_abnahme.py')` — OK
- `py_compile run_vollkreis_abnahme.py` — OK
- **Nacharbeit Pipeline / Zero-Trust:** `verify_vps_docker_port_contract` in `verify_vps_stack`; `verify_docs_chroma_port_drift`; Block **J** Vollkreis; `pytest tests/test_vps_docker_port_contract.py` — 4 passed; `python -m src.scripts.verify_vps_stack` — Exit 0 (live VPS).
- **Anti-Heroin:** `pytest tests/test_run_anti_heroin_scan.py` — passed; `vps_deploy_anti_heroin_mirror` in dieser Umgebung **ohne** gültigen SSH-Key → **Permission denied** — finaler `[PASS]` auf dem VPS nur nach Ausführung auf **Dreadnought** mit Key.

## Offen (explizit nicht in dieser Session)

- WP-E2E (WhatsApp, GH→Deploy, Kong→CORE, OC HTTP, Macro-State in DB)
- Anti-Heroin-Deploy: Operator-Befehl `python -m src.scripts.vps_deploy_anti_heroin_mirror` auf Rechner mit Key (nicht Sandbox)
- WP-AXIOM-MATRIX
- Hostinger IP/Port-Mechanismus final live

## Agos-Takt

Drift MACRO vs. Detailfluss: Draft markiert; MASTER bindend für Deploy-Pfad.

---

## Nachtrag 2026-04-08 — VPS Backup, Kong omega-core live, Verify

| Status | Artefakt |
|--------|----------|
| done | `src/scripts/vps_kong_ensure_omega_core_backend.py` — Admin-API: Service `omega-core-backend`, Route `omega-core-status-route` `/status`, idempotent |
| done | `tests/test_vps_kong_ensure_omega_core_backend.py`, `infra/vps/kong/README.md`, `CORE_INVENTORY_REGISTER.md` |
| done | Ablauf: `vps_backup_snapshot` → ensure-Skript → `verify_vps_stack` (Kong Deck-Referenz inkl. omega-core); `anti_heroin_validator` auf dem neuen Skript |

Verifikation (2026-04-08, keine Secrets im Log): `vps_backup_snapshot` Exit **0**; `vps_kong_ensure_omega_core_backend` Exit **0** (zweiter Lauf idempotent: `[OK] bereits vorhanden`); `verify_vps_stack` Exit **0**; Kong-Zeile **`[OK] Kong Deck-Referenz (evolution, /evo, health, omega-core-backend, /status)`**; `anti_heroin_validator` auf neuem Skript OK; `pytest tests/test_vps_kong_ensure_omega_core_backend.py` 3 passed.

---

## Nachtrag — Vollkreis Block G (`CORE_BASE_URL`) & Detailplan Nachschub

| Status | Artefakt |
|--------|----------|
| done | `run_vollkreis_abnahme.py` — Block **G** Agent-Pool: `curl` gegen **`{CORE_BASE_URL}/status`** (wie Block A, `-sk`, Timeout 10) |
| done | `tests/test_run_vollkreis_core_base_url_block_g.py` — Kontrakt kein festes `localhost:8000/status` |
| done | `docs/05_AUDIT_PLANNING/DETAILPLAN_VPS_OMEGA_NACHSCHUB_2026-04-06.md` — Phasen, Rollen, Abgrenzung Kong-Timeout vs. Loopback-Skript |
| done | `docs/03_INFRASTRUCTURE/OMEGA_BACKEND_VPS_SYSTEMD.md` — `verify_vps_omega_backend_http` vs. Kong Proxy `/status` vs. `CORE_BASE_URL` |
| done | `CORE_INVENTORY_REGISTER.md` |

Verifikation: `anti_heroin_validator.validate_file('run_vollkreis_abnahme.py')` OK; `pytest tests/test_run_vollkreis_core_base_url_block_g.py` 1 passed.

---

## Nachtrag — omega_canon_documents (Anker → PostgreSQL)

| Status | Artefakt |
|--------|----------|
| done | `src/db/migrations/001_omega_canon_documents.sql`, Ergänzung `src/db/core_infrastructure.sql` |
| done | `docs/05_AUDIT_PLANNING/MIGRATIONPLAN_OMEGA_WISSEN_DBS.md` |
| done | `src/scripts/sync_omega_canon_registry.py` (DDL idempotent + UPSERT) |
| done | `tests/test_sync_omega_canon_registry.py`, `OMEGA_RESONANCE_ANCHOR.md` §4, KANON, Inventar, Bibliothek |

Verifikation: `pytest tests/test_sync_omega_canon_registry.py`; `python -m src.scripts.sync_omega_canon_registry` → `[OK] omega_canon_documents: 14 Zeilen synchronisiert.`

---

## Nachtrag — MCP final: `get_orchestrator_bootstrap` + Heartbeat `mcp-server`

| Status | Artefakt |
|--------|----------|
| done | `get_orchestrator_bootstrap` in `mcp_omega_state.py` (Kanon + Events + reachability + gaps + recommendations + `task_hint`) |
| done | `InfrastructureSentinel.check_http_server_up`, VPS-Zeile `mcp-server` in `run_once` |
| done | Tests `test_mcp_omega_state`, `test_infrastructure_heartbeat_mcp.py` |
| done | `CANON_REGISTRY_AGENT_BINDUNG.md`, Rule `8_CANON_REGISTRY_PREFLIGHT.mdc`, `MIGRATIONPLAN_OMEGA_WISSEN_DBS.md` §3, KANON, Inventar, Bibliothek |

Verifikation: `pytest tests/test_mcp_omega_state.py tests/test_infrastructure_heartbeat_mcp.py` — PASS.

---

## Nachtrag — Bootstrap 8049 opt-in, Regeln, Skill

| Status | Artefakt |
|--------|----------|
| done | `mcp_omega_state.py`: `OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY`; `dev_workstation_state_proxy_8049`; `reachability_notes`; Modul-Doc Sentinel ≠ 8049 |
| done | `.cursorrules`, `CLAUDE.md`, Producer-Skill, `9_ORCHESTRATOR_BOOTSTRAP_MCP.mdc`, Skill `orchestrator-bootstrap-preflight`, `8_CANON_*` präzisiert |
| done | Doku: `CANON_REGISTRY_AGENT_BINDUNG.md` §5, `STATE_MTLS_PROXY_START.md`, Inventar, `MIGRATIONPLAN` §3 |
| done | Tests `test_mcp_omega_state.py` (+ Gap-Test bei simuliertem Proxy-Down) |

Verifikation: `pytest tests/test_mcp_omega_state.py`; `validate_file('src/scripts/mcp_omega_state.py')` — PASS.

---

## Nachtrag — Phase 2 Kanon → Chroma `core_canon`

| Status | Artefakt |
|--------|----------|
| done | `src/scripts/ingest_omega_canon_chroma.py`, `COLLECTION_CORE_CANON`, `create_chroma_collections_vps`, `OMEGA_CANON_CHROMA_AFTER_SYNC` in `sync_omega_canon_registry` |
| done | Tests `tests/test_ingest_omega_canon_chroma.py` |
| done | `MIGRATIONPLAN_OMEGA_WISSEN_DBS.md` Phase 2, `CORE_CHROMADB_SCHEMA`, `CANON_REGISTRY`, `ZERO_STATE_FIELD_SCHEMA`, KANON, Inventar, Bibliothek, `AGENTS.md` |

Verifikation: `pytest tests/test_ingest_omega_canon_chroma.py`; `python -m src.scripts.ingest_omega_canon_chroma --from-disk --dry-run`; `validate_file` auf Ingest-Skript — PASS.
