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
