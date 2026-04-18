| **evolution-api** | **55775**→8080 | WhatsApp Multi-Device API (ein QR, Session auf VPS). | **Bevorzugter WhatsApp-Pfad:** CORE sendet/empfängt via Evolution REST; Webhook → CORE `/webhook/whatsapp`. Kein HA-Addon nötig. |
| **Evolution API** | Dreadnought | Eingehende WhatsApp-Nachrichten (via Webhook) | Evolution sendet POST an CORE `/webhook/whatsapp` bei MESSAGES_UPSERT. |
| **VPS (Webhook)** | Dreadnought | GitHub-Event, Evolution-Event | `/webhook/github`, `/webhook/whatsapp` (von Evolution). |
| **Scout/HA** | Dreadnought | WhatsApp-Event (Addon), HA-Events | `rest_command` → CORE `/webhook/whatsapp`; HA-Action → `/webhook/ha_action`. |

# VPS KNOTEN UND FLÜSSE (V4 REWORK - 2026-04-18)

**WICHTIGES HANDOVER-UPDATE ZUR FEHLERHAFTEN DOCKER-MIGRATION:**
Am 18. April 2026 wurde die Architektur auf `/opt/omega/` auf dem VPS migriert. Hierbei wurde versäumt, die **Datenbank-Volumes** für Chroma und Postgres (sowie die lokale `requirements.txt` auf Dreadnought) intakt zu lassen.

1. **DER LOKALE ABSTURZ (Dreadnought Port 8000):**
Die lokale OMEGA-Dreadnought Instanz (`uvicorn` auf `127.0.0.1:8000`) ist abgestürzt. Der Endpunkt `/api/dictate` (Voice/Whisper) ist TOT. Ursache: Konflikt in `requirements.txt` zwischen `pydantic` und der alten `chromadb==0.4.24`. Der nächste Operator MUSS das `.venv` oder `venv` aufräumen, `fastapi`, `pydantic v2` und die richtigen ChromaDB-Versionen herstellen.
Der "Schnelle Hack" im Pip-Install hat den Prozess `uvicorn` geliefert, der mit Pydantic-V1-Fehlern stirbt.

2. **DER VPS-DATENVERLUST (Port 8080 Backend):**
Das Backend auf dem VPS läuft, hat aber **keine** Erinnerungen mehr (RAG kaputt, LLM-Tools ins Leere), da die alten Docker-Volumes `chroma-uvmy_chroma-data` und `agi-state_postgres_state_data` nicht in die neue V4-`docker-compose.yml` unter `/opt/omega/core/` gemountet wurden.

3. **SYSTEMGRENZEN (0 und 1):**
0 und 1 sind keine Metaphern für "Zahlen", sondern die fundamentalen Prellwände im Takt-System.
0 = Ingress (Kong / Entry Adapter)
1 = Backend / Triage / Orchestrator

4. **KONG ROUTING ZU OPENCLAW UND WHATSAPP:**
Die eingehende Kommunikation von der Evolution API an Kong muss zu `mtho_agi_core:8080/webhook/whatsapp` geroutet werden. Das UI von OpenClaw muss zu `brain-openclaw-gateway-1:18789/openclaw` geroutet werden.
Kong verwaltet dies über Pfade und `strip_path=false`.
