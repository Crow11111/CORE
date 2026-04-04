# VPS in drei Prüfungen (Snapshot-Verifikation)

**Vektor:** 2210 | **Delta:** 0.049  
**Zweck:** Schnell prüfen, ob der VPS-Stack aus Sicht von Dreadnought erreichbar und konsistent mit dem [Host-Port-Vertrag](VPS_HOST_PORT_CONTRACT.md) ist — **ohne** Secrets ins Repo zu schreiben.

**Voraussetzungen:** Repo-Root `/OMEGA_CORE`, optional `.env` mit `VPS_HOST`, `CHROMA_PORT`, `KONG_ADMIN_URL` (Overrides). Platzhalter `VPS_HOST` unten durch deine Ziel-IP oder den Wert aus `.env` ersetzen.

---

## 1) Integrierter Stack-Check (SSH + HTTP)

Führt u. a. `docker ps` per SSH, Chroma-Heartbeat, Kong-Deck-Abgleich aus (Details: `src/scripts/verify_vps_stack.py`).

```bash
cd /OMEGA_CORE
export PYTHONPATH=/OMEGA_CORE
python -m src.scripts.verify_vps_stack
```

Mit Projekt-venv (empfohlen):

```bash
cd /OMEGA_CORE
PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.scripts.verify_vps_stack
```

---

## 2) Chroma v2 Heartbeat (nur HTTP)

Vertragsport **32779**; alternativ Port aus `.env` (`CHROMA_PORT`), falls bewusst überschrieben.

```bash
# Platzhalter — keinen echten Host committen
curl -sS --max-time 15 "http://VPS_HOST:32779/api/v2/heartbeat"
```

Mit Variable aus der Shell (nach `source .env` oder manuell gesetzt):

```bash
curl -sS --max-time 15 "http://${VPS_HOST}:32779/api/v2/heartbeat"
# oder, wenn CHROMA_PORT in .env gesetzt ist:
curl -sS --max-time 15 "http://${VPS_HOST}:${CHROMA_PORT}/api/v2/heartbeat"
```

Erwartung: HTTP 200 und Antworttext enthält typischerweise `heartbeat` (vgl. `verify_vps_stack`).

---

## 3) Kong Admin API — Services-Liste

Admin-API liegt laut Vertrag auf Host-Port **32777** (nicht den Proxy-Port verwechseln). **Keine** Admin-Tokens oder `.env`-Inhalte in Doku oder Git ablegen; nur lesende GETs.

```bash
curl -sS --max-time 10 "http://VPS_HOST:32777/services"
```

Optional erste Zeilen der JSON-Antwort prüfen (Status 200, Feld `data` mit Services). Für vollständigen Abgleich mit dem Repo siehe `verify_vps_stack` und `infra/vps/kong/kong-deck-reference.yaml`.

---

## Verweise

- Verbindliche Ports: [VPS_HOST_PORT_CONTRACT.md](VPS_HOST_PORT_CONTRACT.md), `src/config/vps_public_ports.py`
- Arbeitspaket / Abnahme-Tasks: `docs/05_AUDIT_PLANNING/AGENT_WORKPACK_MESSBARE_ABNAHME_2026-04-05.md`
