<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: $\Lambda \approx 0.049$
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# VPS-Knoten: Dienste, Zweck, Einbindung

**Referenz:** `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` | **VPS-Übersicht:** `VPS_FULL_STACK_SETUP.md` | **Übergeordnete Landkarte (Clients, MCP, Kreise):** `@docs/02_ARCHITECTURE/LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md`

Alle Docker-Dienste auf dem VPS sind **Teil des geschlossenen Kreises**. Jeder Knoten hat einen definierten Zweck; CORE/Dreadnought nutzt sie nativ und regelbasiert (Push/Pull). Ohne geschlossene Kette (Git, Webhooks, VPS) ist das System nicht betriebsfähig (Showstopper).

**Soll-/Ist-Verkehr (Kong, MCP, „offen“):** `@docs/02_ARCHITECTURE/KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` — konsolidiert, warum Container „Up“ und leeres Kong gleichzeitig vorkommen und wie SSH-MCP vs. Produkt-HTTP zu trennen sind.

**Verbindliche Host-Ports (Deploy darf nicht driftieren):** `@docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md` · **`src/config/vps_public_ports.py`**

---

## 1. Inventar VPS-Container

| Container | Host-Port(s) | Zweck (warum da) | CORE-Nutzung |
|-----------|----------------|------------------|---------------|
| **chroma-uvmy** | **32779**→8000 | Primäre Vektor-DB (Chroma 1.0.15). RAG, StateAnchor, Embeddings. | Dreadnought/Backend: Embedding-Query, Upsert. `CHROMA_HOST`/`CHROMA_PORT`. |
| **openclaw-admin** | **18789** | OC Gehirn: LLM (Gemini/Claude), WhatsApp (Baileys), Agenten. | CORE ruft Gateway (Chat, RAG, Channels); WhatsApp-Events → CORE-Webhook. |
| **openclaw-spine** | **18790** | OC Spine: sauberer Agent ohne Keys; nutzt Admin als Gateway. | Optionale Agenten-Runs; Konfiguration via `check_openclaw_config_vps`. |
| **evolution-api** | **55775**→8080 | WhatsApp Multi-Device API (ein QR, Session auf VPS). | **Bevorzugter WhatsApp-Pfad:** CORE sendet/empfängt via Evolution REST; Webhook → CORE `/webhook/whatsapp`. Kein HA-Addon nötig. |
| **homeassistant** (ha-atlas) | **18123**→8123 | Remote-HA-Instanz; Spiegel Scout-HA für Backup/zentrale Automations. | Optionale zentrale Automations; Scout-HA bleibt primär. |
| **kong** | **32776** (Proxy), **32777** (Admin), **32778** (Manager) | API-Gateway: zentrales Routing, Rate-Limit, Auth vor Diensten. | Optional: CORE/Agenten rufen VPS-Dienste über Kong (ein Einstieg) statt direkte Ports. |
| **monica** | **32772**→80 | Personal CRM: Kontakte, Beziehungen, Aktivitäten. | CORE/Agenten: Kontaktkontext für Antworten, Anrede, Beziehungspflege; API-Anbindung. |
| **atlas_agi_core** | **8080** | AGI-State Persistenz-Layer (App/Service). | State-Anfragen, Kontext-Sync; Skripte wie `deploy_agi_state.py`. |
| **atlas_chroma_state** | intern | ChromaDB 0.4.24 (Legacy AGI-State). | Legacy-RAG/State; Migration zu chroma-uvmy möglich. |
| **atlas_postgres_state** | intern | PostgreSQL 15 + pgvector. Strukturierte AGI-State-Daten. | Multi-View, strukturierte Abfragen; `multi_view_client.py`, `deploy_multiview_schema.py`. |
| **mcp-server** | **8001** | MCP-Server für Tool-Integration (Cursor, Agenten). | Cursor: MCP „atlas-remote“; Zugriff auf VPS-Workspace, Tools. |
| **openclaw-wslc** (Hostinger) | **55800**, **58105** (hvps) | Hostinger One-Click OpenClaw. | Optionale zweite OC-Instanz(en) — kanonisch: eine Instanz definieren. |

---

## 2. Was zieht (Pull) – wer holt was, wann

| Von (Quelle) | Nach (Ziel) | Was | Wann / Trigger |
|--------------|-------------|-----|-----------------|
| **Chroma (VPS)** | Dreadnought/Backend | Vektoren, Similarity-Search | Jede RAG-/Gravitator-Anfrage; Embedding-Upsert nach Ingest. |
| **Postgres (atlas_postgres_state)** | Dreadnought/Backend | Strukturierte State-Daten, Multi-View | `multi_view_client.py`, Reports, Konvergenz-Daten. |
| **OpenClaw Admin** | Dreadnought | Agent-Ergebnisse, Channel-Status | API-Calls von CORE (Chat-Completion, RAG), Status-Check. |
| **Evolution API** | Dreadnought | Eingehende WhatsApp-Nachrichten (via Webhook) | Evolution sendet POST an CORE `/webhook/whatsapp` bei MESSAGES_UPSERT. |
| **HA (Scout)** | Dreadnought | Events, States, Service-Antworten | Backend ruft `HASS_URL` (Lights, WhatsApp send via HA falls kein Evolution). |
| **Monica** | Dreadnought/Agenten | Kontakte, Aktivitäten | Bei Kontext-Anreicherung (z. B. Anrede, letzte Interaktion). |
| **GitHub** | VPS | Repo-Inhalt (push-Event) | Webhook `/webhook/github` → `git pull` in GIT_PULL_DIR; Build-Engine/Takt 4. |
| **MCP (VPS)** | Cursor | Workspace, Tools | Cursor fragt MCP-Server an; Lese/Schreib-Tools. |
**GitHub-Webhook auf dem VPS:** Der Empfang des Webhooks (POST `/webhook/github`) erfolgt durch die CORE FastAPI-App (`src/api/routes/github_webhook.py`). Damit der VPS den Pull ausführt, muss diese API (oder ein schlanker Dienst mit nur dieser Route) **auf dem VPS** laufen; in GitHub ist die Payload-URL auf `https://<VPS-Host>:<Port>/webhook/github` zu setzen, und auf dem VPS müssen `GIT_PULL_DIR` und `GITHUB_WEBHOOK_SECRET` in der Umgebung gesetzt sein. Alternativ: separater Listener auf dem VPS (manuell konfigurieren).



---

## 3. Was drückt (Push) – wer sendet wohin, wann

| Von (Quelle) | Nach (Ziel) | Was | Wann / Trigger |
|--------------|-------------|-----|-----------------|
| **Dreadnought** | Chroma (VPS) | Embeddings, Dokument-Chunks | Ingest-Skripte, StateAnchor-Update. |
| **Dreadnought** | OpenClaw Admin | Chat-Request, RAG-Query, Mirror-Events | Webhook-Verarbeitung, `_mirror_to_oc_brain`, Trigger-Tasks. |
| **Dreadnought** | Evolution API | WhatsApp-Nachricht (sendText) | Nach Triage/LLM: Antwort an User; `EvolutionClient.send_text()` (wenn konfiguriert). |
| **Dreadnought** | HA (Scout) | Service-Calls (Licht, WhatsApp send) | `ha_client.send_whatsapp`, `call_service`; bei Command-Triage. |
| **Dreadnought** | GitHub | Code/Config (commit + push) | Nach Takt 3 (Arbeiten); schließt Kurbelwelle (Takt 4). |
| **Dreadnought** | VPS (Backup) | Backup-Artefakte | `daily_backup.py`, SFTP/rsync nach `/var/backups/core`. |
| **VPS (Webhook)** | Dreadnought | GitHub-Event, Evolution-Event | `/webhook/github`, `/webhook/whatsapp` (von Evolution). |
| **Scout/HA** | Dreadnought | WhatsApp-Event (Addon), HA-Events | `rest_command` → CORE `/webhook/whatsapp`; HA-Action → `/webhook/ha_action`. |
| **OpenClaw** | Dreadnought | Agent-Output, Channel-Callback | Webhook/Callback-URL in OC-Config. |

---

## 4. Einbindung in den Prozess

- **Kong:** Alle externen Aufrufe zum VPS können über Kong laufen (ein Host, verschiedene Routes). CORE `.env`: z. B. `VPS_GATEWAY_URL=http://VPS:32773` statt direkter Ports; Kong routet zu Chroma, OC, Evolution, Monica.
- **Monica:** Kontakt-API (REST). CORE/Agenten vor Antwort an User: „Wer ist der Absender?“ → Monica-API abfragen → personalisierte Anrede/Kontext. `.env`: `MONICA_URL`, `MONICA_TOKEN` (falls genutzt).
- **Evolution API:** Primärer WhatsApp-Kanal. CORE sendet Antworten via `POST /message/sendText/{instance}`; Evolution sendet eingehende Nachrichten an CORE-Webhook. Ein QR auf VPS; kein erneuter Scan bei OS-Wechsel. `.env`: `EVOLUTION_API_URL`, `EVOLUTION_INSTANCE`, `EVOLUTION_API_KEY`.
- **atlas_agi_core / Postgres / Chroma-State:** AGI-State und Multi-View laufen über bestehende Skripte (`deploy_agi_state.py`, `multi_view_client.py`). Backend kann Postgres/Chroma für strukturierte Abfragen anbinden.

---

## 5. Verifikation

| Knoten | Prüfung |
|--------|---------|
| chroma-uvmy | `curl http://$VPS_HOST:32779/api/v2/heartbeat` |
| openclaw-admin | `curl http://$VPS_HOST:18789/api/status` |
| evolution-api | `curl -H "apikey: $EVOLUTION_API_KEY" http://$VPS_HOST:55775/instance/fetchInstances` (oder Instanz-Status) |
| monica | `curl -H "Authorization: Bearer $MONICA_TOKEN" http://$VPS_HOST:32772/api/contacts` (wenn konfiguriert) |
| kong | `curl http://$VPS_HOST:32777/status` (Kong Admin API) |
| mcp-server | Cursor MCP „atlas-remote“ starten; Workspace-Zugriff |

Siehe auch: `python -m src.scripts.verify_vps_stack` (optionale Knoten Evolution, Monica, Kong werden bereits geprüft: Container + HTTP-Erreichbarkeit).

---

## 6. Soll vs. Ist: WhatsApp-Ausgang (Evolution vs. HA)

| Aspekt | Soll (Ziel) | Ist (Stand) |
|--------|-------------|-------------|
| **Bevorzugter Pfad** | Evolution API auf VPS: CORE sendet via `EvolutionClient.send_text()` an Evolution; eingehend via Evolution-Webhook → `/webhook/whatsapp`. | Nur HA-Pfad implementiert: `HAClient.send_whatsapp()`; Webhook-Empfang von HA (rest_command) und (theoretisch) Evolution gleicher Endpoint `/webhook/whatsapp`. |
| **.env** | `EVOLUTION_API_URL`, `EVOLUTION_INSTANCE`, `EVOLUTION_API_KEY` (siehe §4). | Optionale Platzhalter in `.env`; ungesetzt = Fallback auf VPS_HOST:55775 in `verify_vps_stack.py`. |
| **Abnahme D** | Verifikation: Evolution, Monica, Kong als optionale Checks lauffähig. | `verify_vps_stack.py` führt optionale Container- und HTTP-Checks für Evolution, Monica, Kong aus; Exit 0 auch wenn optional nicht erreichbar. |

**Fazit:** Für die Vollkreis-Abnahme Bereich D reicht die bestehende Verifikation (optionale Checks). Umschaltung auf Evolution als Sende-Pfad erfordert Implementierung eines Evolution-Clients und Triage im Webhook/Notification-Pfad (wenn Evolution konfiguriert → send_text; sonst HA send_whatsapp).

---

## 7. Referenzen

- VPS_FULL_STACK_SETUP.md (Deploy, Firewall, Ports)
- WHATSAPP_E2E_HA_SETUP.md (HA-Pfad); Evolution = alternativer/bevorzugter Pfad
- OMEGA_LINUX_ORCHESTRATION.md (Topologie, Testmatrix)
- G_CORE_CIRCLE.md (Git-Webhook-Kurbelwelle)
