<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# VPS-Knoten: Dienste, Zweck, Einbindung

**Referenz:** `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` | **VPS-Übersicht:** `VPS_FULL_STACK_SETUP.md`

Alle Docker-Dienste auf dem VPS sind **Teil des geschlossenen Kreises**. Jeder Knoten hat einen definierten Zweck; CORE/Dreadnought nutzt sie nativ und regelbasiert (Push/Pull). Ohne geschlossene Kette (Git, Webhooks, VPS) ist das System nicht betriebsfähig (Showstopper).

---

## 1. Inventar VPS-Container

| Container | Port | Zweck (warum da) | CORE-Nutzung |
|-----------|------|------------------|---------------|
| **chroma-uvmy** | 32768 | Primäre Vektor-DB (Chroma 1.0.15). RAG, StateAnchor, Embeddings. | Dreadnought/Backend: Embedding-Query, Upsert. `CHROMA_HOST`/`CHROMA_PORT`. |
| **openclaw-admin** | 18789 | OC Gehirn: LLM (Gemini/Claude), WhatsApp (Baileys), Agenten. | CORE ruft Gateway (Chat, RAG, Channels); WhatsApp-Events → CORE-Webhook. |
| **openclaw-spine** | 18790 | OC Spine: sauberer Agent ohne Keys; nutzt Admin als Gateway. | Optionale Agenten-Runs; Konfiguration via `check_openclaw_config_vps`. |
| **evolution-api** | 55775 | WhatsApp Multi-Device API (ein QR, Session auf VPS). | **Bevorzugter WhatsApp-Pfad:** CORE sendet/empfängt via Evolution REST; Webhook → CORE `/webhook/whatsapp`. Kein HA-Addon nötig. |
| **homeassistant** (ha-atlas) | 18123 | Remote-HA-Instanz; Spiegel Scout-HA für Backup/zentrale Automations. | Optionale zentrale Automations; Scout-HA bleibt primär. |
| **kong** | 32773–32775 | API-Gateway: zentrales Routing, Rate-Limit, Auth vor Diensten. | Optional: CORE/Agenten rufen VPS-Dienste über Kong (ein Einstieg) statt direkte Ports. |
| **monica** | 32769 | Personal CRM: Kontakte, Beziehungen, Aktivitäten. | CORE/Agenten: Kontaktkontext für Antworten, Anrede, Beziehungspflege; API-Anbindung. |
| **atlas_agi_core** | 8080 | AGI-State Persistenz-Layer (App/Service). | State-Anfragen, Kontext-Sync; Skripte wie `deploy_agi_state.py`. |
| **atlas_chroma_state** | intern | ChromaDB 0.4.24 (Legacy AGI-State). | Legacy-RAG/State; Migration zu chroma-uvmy möglich. |
| **atlas_postgres_state** | intern | PostgreSQL 15 + pgvector. Strukturierte AGI-State-Daten. | Multi-View, strukturierte Abfragen; `multi_view_client.py`, `deploy_multiview_schema.py`. |
| **mcp-server** | 8001 | MCP-Server für Tool-Integration (Cursor, Agenten). | Cursor: MCP „atlas-remote“; Zugriff auf VPS-Workspace, Tools. |
| **openclaw-wslc** (Hostinger) | 55800 | Hostinger One-Click OpenClaw. | Optionale zweite OC-Instanz. |

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
| chroma-uvmy | `curl http://$VPS_HOST:32768/api/v2/heartbeat` |
| openclaw-admin | `curl http://$VPS_HOST:18789/api/status` |
| evolution-api | `curl -H "apikey: $EVOLUTION_API_KEY" http://$VPS_HOST:55775/instance/fetchInstances` (oder Instanz-Status) |
| monica | `curl -H "Authorization: Bearer $MONICA_TOKEN" http://$VPS_HOST:32769/api/contacts` (wenn konfiguriert) |
| kong | `curl http://$VPS_HOST:32773/status` (Kong Admin API) |
| mcp-server | Cursor MCP „atlas-remote“ starten; Workspace-Zugriff |

Siehe auch: `python -m src.scripts.verify_vps_stack` (erweiterbar um optionale Knoten).

---

## 6. Referenzen

- VPS_FULL_STACK_SETUP.md (Deploy, Firewall, Ports)
- WHATSAPP_E2E_HA_SETUP.md (HA-Pfad); Evolution = alternativer/bevorzugter Pfad
- OMEGA_LINUX_ORCHESTRATION.md (Topologie, Testmatrix)
- G_CORE_CIRCLE.md (Git-Webhook-Kurbelwelle)
