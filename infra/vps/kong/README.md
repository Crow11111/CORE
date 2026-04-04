# Kong — deklarative Referenz (Repo)

**Verpflichtende Planquelle:** `docs/02_ARCHITECTURE/KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` **§8.3** — Services und Routes **als Code** im Repo; Verifikation in `verify_vps_stack.py`.


| Datei                      | Zweck                                                                                                                                  |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `kong-deck-reference.yaml` | Spiegelt den **genehmigten** Kong-Stand (Ist messbar über Admin-API). Kein blindes `deck sync` gegen Produktion ohne Operator-Abnahme. |


**VPS-Pfade zum laufenden Compose:** `docs/03_INFRASTRUCTURE/VPS_COMPOSE_PATHS.md`.

**Backup vor Infra-Änderungen:** `python -m src.scripts.vps_backup_snapshot` — Plan: `docs/05_AUDIT_PLANNING/VPS_UMSETZUNGSPLAN_BACKUP_KONG_HEALTH.md`.

**Kong `/health` idempotent anlegen:** `python -m src.scripts.vps_kong_ensure_health_route`.