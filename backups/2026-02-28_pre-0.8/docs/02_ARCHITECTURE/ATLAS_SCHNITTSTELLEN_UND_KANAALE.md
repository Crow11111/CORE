# ATLAS Schnittstellen & Kanäle – Abstimmung OC Brain ↔ Dreadnought

**Zweck:** Zentrale Referenz für alle Verbindungen und Kanäle, die ATLAS (OC Brain, Dreadnought, Scout, WhatsApp, ChromaDB) benötigt. Abgestimmt mit ARCHITECTURE.md (ATLAS Neocortex V1.0).

---

## 1. Übersicht

| Kanal | A → B | Protokoll | Konfiguration (.env / VPS) |
|-------|--------|-----------|----------------------------|
| **Dreadnought → OC Brain** | ATLAS_CORE → Gateway | HTTPS (Nginx) oder HTTP | VPS_HOST, OPENCLAW_GATEWAY_TOKEN, OPENCLAW_GATEWAY_HTTPS=1, OPENCLAW_GATEWAY_PORT=443 |
| **OC Brain → Dreadnought** | OC → ATLAS (Rat) | SSH + SFTP (Abholung) | VPS_HOST, OPENCLAW_RAT_SUBMISSIONS_DIR, fetch_oc_submissions |
| **Scout → OC Brain** | HA/Scout → Gateway | HTTPS POST /v1/responses | Wie Dreadnought; gleicher Endpunkt mit Token |
| **OC Brain ↔ WhatsApp** | Gateway ↔ Meta | OpenClaw-Kanal | channels.whatsapp, allowFrom; Pairing (QR) in UI |
| **Dreadnought ↔ ChromaDB** | ATLAS_CORE ↔ Vektor-DB | HTTP (VPS) oder lokal | CHROMA_HOST, CHROMA_PORT (VPS: 187.77.68.250 oder SSH-Tunnel) |

---

## 2. Dreadnought → OC Brain (ATLAS spricht mit OC)

- **Endpoint:** `POST /v1/responses` (OpenResponses-kompatibel).
- **URL:**  
  - Mit Nginx (empfohlen): `https://187.77.68.250` (Port 443).  
  - In .env: `OPENCLAW_ADMIN_VPS_HOST=187.77.68.250`, `OPENCLAW_GATEWAY_HTTPS=1`, `OPENCLAW_GATEWAY_PORT=443`.
  - Ohne HTTPS: `http://187.77.68.250:18789`.
- **Header:** `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>`, `x-openclaw-agent-id: main`.
- **Body:** `{"model": "openclaw", "input": "<Nachricht oder JSON-String>"}`.
- **Code:** `src/network/openclaw_client.py` – `send_message_to_agent(text, agent_id="main")`.
- **API-Route:** `POST /api/oc/send` (Backend), Body: `{"text": "...", "agent_id": "main"}`.

---

## 3. OC Brain → Dreadnought (OC → Rat / ATLAS)

- **Mechanismus:** OC (oder Agent) legt JSON-Dateien im Workspace ab; ATLAS holt sie per SSH.
- **Pfad auf VPS (Host):** `/opt/atlas-core/openclaw-admin/data/workspace/rat_submissions/`.
- **Im Container:** `/home/node/.openclaw/workspace/rat_submissions/`.
- **.env:** `OPENCLAW_RAT_SUBMISSIONS_DIR=/opt/atlas-core/openclaw-admin/data/workspace/rat_submissions` (optional, Default bereits gesetzt).
- **Abholung:** `python -m src.scripts.fetch_oc_submissions` oder `GET/POST /api/oc/fetch`.
- **Schema:** `{"from":"oc","type":"rat_submission","created":"ISO8601","payload":{"topic":"...","body":"..."}}`.

---

## 4. Scout → OC Brain (Webhook für Events)

- **Gleicher Endpunkt wie Dreadnought:** `POST https://187.77.68.250/v1/responses` (mit Nginx).
- **Header:** `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>`, `x-openclaw-agent-id: main`.
- **Body:** Event als Text oder JSON-String im `input`-Feld, z. B.:
  `{"model":"openclaw","input":"{\"source\":\"scout\",\"node_id\":\"raspi5-ha-master\",\"event_type\":\"motion_detected_prefiltered\",\"data\":{...}}"}`.
- **Scout/HA:** Automation oder Skript auf dem Raspi sendet HTTPS-POST an `https://187.77.68.250/v1/responses` mit Token (aus sicherem Speicher).

---

## 5. WhatsApp (OC Brain)

- **Konfiguration:** OpenClaw `channels.whatsapp` in `openclaw.json` (allowFrom, dmPolicy).
- **Pairing:** Einmalig in der Control-UI (https://187.77.68.250/#token=...) unter Channels → WhatsApp → QR scannen oder Pairing-Code.
- **.env:** `WHATSAPP_TARGET_ID` (z. B. 491788360264) für allowFrom; beim Deploy übernommen.
- **Aus OC Brain:** Nachrichten versenden/empfangen über das message-Tool (siehe OpenClaw-Docs).

---

## 6. ChromaDB (Vektor-DB für ATLAS)

- **Nutzung:** ATLAS_CORE (Dreadnought) und ggf. spätere Dienste; OC Brain hat keine direkte ChromaDB-Integration im Standard-OpenClaw.
- **Lokal:** `CHROMA_HOST` leer → `CHROMA_LOCAL_PATH` (z. B. `c:\MTHO_CORE\data\chroma_db`).
- **Remote (VPS):** `CHROMA_HOST=187.77.68.250`, `CHROMA_PORT=8000`.  
  **Hinweis:** Port 8000 auf dem VPS ist per UFW geschlossen (nur intern). Zugriff von Dreadnought: SSH-Tunnel `ssh -L 8000:127.0.0.1:8000 root@187.77.68.250`, dann lokal `CHROMA_HOST=localhost`, `CHROMA_PORT=8000`.
- **Collections (laut ARCHITECTURE):** `events`, `insights`; zusätzlich bestehend: `argos_knowledge_graph`, `core_brain_registr` (siehe chroma_client.py).
- **Init:** `python -m src.db.init_chroma` (für user_state_vectors); bei Bedarf Collections `events`/`insights` manuell oder per Skript anlegen.

---

## 7. Voice (ElevenLabs) – unabhängig von WhatsApp

- **POST /api/atlas/tts:** Body `{ "text": "...", "role": "atlas_dialog"|"analyst"|..., "state_prefix": "" }` → Audio/MP3 zurück. Rollen aus `voice_config.OSMIUM_VOICE_CONFIG`.
- **GET /api/atlas/voice/roles:** Liste aller Rollen (Stimmen).
- **.env:** `ELEVENLABS_API_KEY`. Automatisierung: Jeder Client (OC Brain, Scout, HA) kann TTS auslösen; verschiedene Stimmen über `role`.

---

## 8. Checkliste Einrichtung

1. **.env (Dreadnought):**
   - `OPENCLAW_ADMIN_VPS_HOST=187.77.68.250` (oder VPS_HOST)
   - `OPENCLAW_GATEWAY_TOKEN=<Token>`
   - `OPENCLAW_GATEWAY_HTTPS=1` und `OPENCLAW_GATEWAY_PORT=443` (bei Nginx)
   - Optional: `OPENCLAW_RAT_SUBMISSIONS_DIR=/opt/atlas-core/openclaw-admin/data/workspace/rat_submissions`
   - `CHROMA_HOST` / `CHROMA_PORT` bei Remote-ChromaDB (oder Tunnel)

2. **VPS:** Deploy ausgeführt → `rat_submissions` existiert, ARCHITECTURE.md + SOUL.md im Workspace.

3. **WhatsApp:** In OC UI pairen (QR oder Pairing-Code); allowFrom in Config passt.

4. **Test:**  
   - `GET /api/oc/status` oder `python -c "from src.network.openclaw_client import check_gateway; print(check_gateway())"`  
   - `POST /api/oc/send` mit `{"text":"Ping"}`.  
   - `GET /api/oc/fetch` zum Abholen von Rat-Einreichungen.
