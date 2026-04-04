# VPS Host-Port-Vertrag (Single Source of Truth)

**Vektor:** 2210 | **Delta:** 0.049  
**Status:** VERBINDLICH für Deploy, Code-Defaults und Schnittstellendoku  
**Code:** `src/config/vps_public_ports.py` (importieren, nicht duplizieren)

---

## 1. Für wen ist dieses Dokument?


| Rolle                          | Pflicht                                                                                                                                                                                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Operator / Architekt / PM**  | Kenntnis: *Es gibt einen festen Vertrag.* Kein manuelles Port-Gefrickel. Abweichung = **Infra-Bug oder bewusster Vertragswechsel**.                                                                                                                                                   |
| **Producer / Agenten / Infra** | Jeder Deploy auf dem VPS **muss** diese Host-Ports publizieren (Docker `ports: "HOST:CONTAINER"`). Nach jeder Änderung: **dieses Dokument**, `vps_public_ports.py`, `VPS_KNOTEN_UND_FLUSSE.md`, `VPS_FULL_STACK_SETUP.md`, Verifikationsskripte **im selben Änderungssatz** anpassen. |
| **Auditor**                    | `docker ps` auf dem VPS **gegen** diese Tabelle prüfen. Abweichung ohne Repo-Update = **Drift / VETO-Würdig**.                                                                                                                                                                        |


---

## 2. Vertragliche Host-Ports (Stand: Abgleich mit VPS 2026-04-04)

Host-Port ist die Zahl **links** in `0.0.0.0:HOST->CONTAINER/tcp`.


| Dienst                      | Host-Port | Container-Port | Stack-Hinweis                                               |
| --------------------------- | --------- | -------------- | ----------------------------------------------------------- |
| Chroma 1.0.15 (chroma-uvmy) | **32779** | 8000           | `chroma-uvmy-chromadb-1`                                    |
| Kong Proxy                  | **32776** | 8000           | `kong-s7rk-kong-1`                                          |
| Kong Admin API              | **32777** | 8001           | dito                                                        |
| Kong Manager UI             | **32778** | 8002           | dito                                                        |
| Evolution API               | **55775** | 8080           | `evolution-api-yxa5-api-1`                                  |
| OpenClaw Admin (kanonisch)  | **18789** | 18789          | `openclaw-admin`                                            |
| OpenClaw Spine              | **18790** | 18790          | `openclaw-spine`                                            |
| MCP-Server                  | **8001**  | 8001           | `mcp-server`                                                |
| Monica                      | **32772** | 80             | `monica-0mip-monica-1`                                      |
| Home Assistant (ha-atlas)   | **18123** | 8123           | `ha-atlas`                                                  |
| atlas_agi_core              | **8080**  | 8080           | `atlas_agi_core`                                            |
| Hostinger OpenClaw (hvps)   | **58105** | 58105          | parallel — Architektur: auf **eine** OC-Instanz fokussieren |
| Hostinger OpenClaw (wslc)   | **55800** | 55800          | dito                                                        |


**Ohne Host-Mapping (nur intern):** `atlas_postgres_state`, `atlas_chroma_state`, Kong-DB, Monica-DB, Evolution-Postgres/Redis — **Ost–West** im Docker-Netz.

---

## 3. Docker Compose — Vernagelung (Muster)

Im jeweiligen `docker-compose.yml` auf dem VPS **explizit** (kein zufälliges Host-Mapping):

```yaml
# Beispiel Chroma — Host-Port MUSS dem Vertrag entsprechen
services:
  chromadb:
    image: chromadb/chroma:1.0.15
    ports:
      - "32779:8000"
```

Gleiches Prinzip für Kong (**32776–32778**), Evolution (**55775:8080**), usw. Wenn Hostinger ein UI zur Portwahl anbietet: Werte **auf diese Tabelle** setzen, nicht umgekehrt.

---

## 4. `.env` auf Dreadnought

Optional Overrides bleiben möglich (`CHROMA_PORT`, `KONG_ADMIN_URL`, …). **Soll:** Werte = Vertrag, damit Defaults aus `vps_public_ports.py` und Skripte **ohne** `.env` korrekt bleiben.

**Plan §8.4:** Overrides nur bewusst; optional `VPS_GATEWAY_URL`, wenn alles über Kong laufen soll (noch nicht global erzwungen). **SSH/Deploy:** `VPS_HOST`, `VPS_SSH_KEY` — siehe `verify_vps_stack.py`. **Compose-Pfade auf dem VPS:** `docs/03_INFRASTRUCTURE/VPS_COMPOSE_PATHS.md`.

---

## 5. Verifikation

- `python -m src.scripts.verify_vps_stack` — nutzt Vertrags-Defaults aus `vps_public_ports.py`; prüft bei laufendem Kong die **Deck-Referenz** (`infra/vps/kong/kong-deck-reference.yaml`: Service `evolution-api`, Route `/evo`).
- `run_vollkreis_abnahme.py` — Block D/Gk Chroma gegen Vertrag.
- Bei **Infrastructure-Change:** erneut `docker ps` ziehen; wenn Ports gleich → nur Timestamp im Archiv (`KONSOLIDIERTER_VERKEHRSPLAN` Anhang) erneuern; wenn Ports weichen → **Vertrag** oder **Deploy** reparieren — nie stilles Driften.

---

[PASS] VPS Host-Port-Vertrag — Pflegepflicht Agenten/Infra; Operator nur Abnahme gegen Tabelle.