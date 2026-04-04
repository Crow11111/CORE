# VPS — Verifikationsauszug (Nachweis, kein Geheimnis)

**Zeitpunkt:** 2026-04-04 (nach Backup `20260404T123603Z` und Anlage Kong `/health`)

**Befehle (lokal, mit `.env`):**

1. `python -m src.scripts.vps_backup_snapshot`
2. `python -m src.scripts.vps_kong_ensure_health_route`
3. `curl -sS http://<VPS_HOST>:32776/health` → erwarteter Body: `OMEGA_KONG_HEALTH_OK`
4. `python -m src.scripts.verify_vps_stack`

**Letzte `verify_vps_stack`-Ausgabe (Auszug):**

```
[OK] openclaw-admin
[OK] chroma-uvmy-chromadb
[OK] mcp-server
[OK] ha-atlas
[OK] (optional) evolution-api
[OK] (optional) monica
[OK] (optional) kong
  Container gesamt: 17
[OK] Kong Deck-Referenz (evolution-api, /evo, omega-kong-health, /health)
[OK] Kong Proxy /health (HTTP + Body)
[OK] Chroma v2 heartbeat
[OK] (optional) Evolution API erreichbar
[OK] (optional) Monica erreichbar
[OK] (optional) Kong erreichbar
```

**Rollback Health-Service (auf dem VPS):** siehe `VPS_UMSETZUNGSPLAN_BACKUP_KONG_HEALTH.md`.

**Hinweis Screenshot:** Kong Manager (`:32778`) im eingebetteten Cursor-Browser erreichte hier nur `about:blank` (Sandbox/Netz). Sichtbarer Nachweis: Terminal `curl …/health` und die Ausgabe von `verify_vps_stack` oben; im eigenen Browser `http://<VPS_HOST>:32778` öffnen.
