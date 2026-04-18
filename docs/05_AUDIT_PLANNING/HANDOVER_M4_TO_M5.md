# HANDOVER: M5 - CLOSING THE MECHANICAL LOOP

**Datum:** 2026-04-18
**Ziel:** OMEGA in den produktiven Initialzustand versetzen, indem der mechanische Loop (Evolution -> Kong -> Backend -> OpenClaw) physisch geschlossen und das lokale Entwicklungs-System repariert wird. Keine Prosa, nur Code und Topologie.

## STATUS QUO (Was defekt ist)
1. **LOKAL (Dreadnought):** Das Python `.venv` ist zerstört. `pip install` mit inkompatiblen Chroma/Pydantic-Versionen hat das lokale FastAPI/Uvicorn zerschossen. `POST /api/dictate` (Voice) funktioniert nicht.
2. **VPS (Backend Amnesie):** Die Container in `/opt/omega/core/` laufen, aber sie nutzen leere Volumes. Die historischen Daten (RAG) liegen ungenutzt in `chroma-uvmy_chroma-data` und `agi-state_postgres_state_data`.
3. **VPS (OpenClaw):** OpenClaw läuft in V4 (`/opt/omega/brain/`) und hat sein altes Gedächtnis (Config/Token) erfolgreich implantiert bekommen. Kong leitet `/openclaw` dorthin.

## DIE NÄCHSTEN SCHRITTE FÜR DEN AGENTEN

**Schritt 1: Reparatur Dreadnought (Lokal)**
- Analysiere die Konflikte in `src/requirements.txt` zwischen `pydantic` (v1/v2), `fastapi` und `chromadb==0.4.24`.
- Baue das lokale `.venv` neu auf, bis `uvicorn src.api.main:app` fehlerfrei bootet und `/api/dictate` wieder erreichbar ist.

**Schritt 2: Heilung des VPS-Gedächtnisses**
- Verbinde dich via SSH (`root@187.77.68.250`).
- Ändere `/opt/omega/core/docker-compose.yml`, sodass die Volumes `chroma_data` und `postgres_data` als `external: true` deklariert werden und auf die alten, befüllten Volumes zeigen.
- `docker compose down && docker compose up -d`.

**Schritt 3: Schließen des mechanischen Loops (Der Test)**
- Sende eine WhatsApp-Nachricht an die Evolution-API.
- Verfolge die Logs: Evolution -> Kong -> `mtho_agi_core` (`/webhook/whatsapp`) -> OpenClaw.
- Sobald das System selbstständig antwortet und diesen Vorfall dokumentiert, ist der Loop geschlossen. Erst dann greifen die Regeln.
