# VPS: Umsetzungsplan — Backup, Kong-Health, Nachweis

**Ziel (verständlich):** Bevor Kong geändert wird, liegt auf dem VPS ein **Zeitstempel-Ordner** mit Kopien (Kong-JSON, `docker ps`, Compose-Dateien). Danach kommt **eine** zusätzliche Route **`/health`** am Kong-Proxy, die **ohne** Backend nur `OMEGA_KONG_HEALTH_OK` zurückgibt — damit du im Browser oder mit `curl` **sofort** siehst, dass der Proxy wirklich antwortet. Evolution bleibt unter **`/evo`** unverändert.

**Was das nicht ist:** Kein vollständiger WhatsApp→CORE→Kong-End-to-End-Test (braucht öffentliche Webhook-URL und Evolution-Konfiguration).

---

## Phase 0 — Risiko

Änderungen nur **additiv** (neuer Service + Route + Plugin). Rollback: Service löschen (Kong entfernt Routen/Plugins mit).

---

## Phase 1 — Backup (auf dem VPS)

Skript: `python -m src.scripts.vps_backup_snapshot`

Speicherort: `/root/omega-core-backups/<UTC-Zeitstempel>/`

Inhalt u. a.:

- `docker_ps.txt`
- `kong_services.json`, `kong_routes.json`, `kong_plugins.json` (von `127.0.0.1:32777`)
- Kopien der gefundenen `docker-compose.yml` unter `/docker/…` und `/opt/atlas-core/mcp-server/`

---

## Phase 2 — Kong `/health` (idempotent)

Skript: `python -m src.scripts.vps_kong_ensure_health_route`

- Wenn Service `omega-kong-health` schon existiert → nichts tun.
- Sonst: Dummy-`url` (wird durch Plugin nicht genutzt), Route `/health`, Plugin `request-termination` → 200 + Body `OMEGA_KONG_HEALTH_OK`.

---

## Phase 3 — Nachweis

- `python -m src.scripts.verify_vps_stack` muss u. a. **`[OK] Kong Proxy /health`** ausgeben.
- Optional manuell: `curl -sS http://<VPS_HOST>:32776/health`

---

## Rollback (manuell auf dem VPS)

```bash
# Admin von localhost auf dem VPS (Port siehe Vertrag)
curl -sS -X DELETE "http://127.0.0.1:32777/services/omega-kong-health"
```

Bei größerem Schaden: Kong-JSON aus dem Backup-Ordner mit Admin-API oder Deck wieder einspielen (nicht automatisiert in diesem Ticket).
