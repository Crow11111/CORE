# ATLAS Kern-Context (Token-reduziert)

Kompakte Referenz für Chat/Orchestrator. Details in verlinkten Docs.

---

## Teamchef / Orchestrator
- **Du gibst die Ziele vor.** Böser Einpeitscher: nur harte Antworten, nur Beweise. Du glaubst gar nichts – alles verifizieren. Ungeprüft weitergeben = Systemschaden.
- Teams parallel, Token-Druck, Informationsdefizit. Ziel: ATLAS steht.

## Prototyp 0.8 Stand
- **Läuft:** ATLAS hört (Pipeline), sieht (Fallback), spricht (TTS/WA). OC Brain, Event-Ingest, Spine↔Brain, Task-Loop, rat_submissions.
- **Beweis:** `python -m src.scripts.proof_hoert_sieht_spricht` -> Alles OK (Stand 28.02.2026).
- **Offen:** Echtzeit-Audio (Hardware), Vision-Analyse der Bilder, direkte HA-Steuerung.

## Wichtigste Endpoints
| Was | Wo |
|-----|-----|
| OC Brain | http://187.77.68.250:18789, POST /v1/responses, Header x-openclaw-agent-id: main, Bearer token |
| Event-Ingest | POST /api/atlas/event (source, node_id, event_type, data) |
| TTS | POST /api/atlas/tts (text, role), GET /api/atlas/voice/roles |
| Status | GET /api/atlas/status |

## Wichtigste Skripte
- `e2e_event_to_tts` (Z13: Event→OC→TTS), `scout_send_event_to_oc` (Event an OC Brain), `test_dreadnought_pipeline` (OC + Voice + Event), `test_atlas_speak` (TTS + WhatsApp), `send_audio_to_whatsapp` (MP3 via HA), `fetch_oc_submissions` (OC→ATLAS), `deploy_vps_full_stack` (VPS-Deploy).

## .env-Kern
- OPENCLAW_ADMIN_VPS_HOST, OPENCLAW_GATEWAY_TOKEN, OPENCLAW_GATEWAY_PORT=18789; HASS_URL, HASS_TOKEN, WHATSAPP_TARGET_ID; ELEVENLABS_API_KEY; CHROMA_HOST optional.

## Ziele (Teamchef): ATLAS hört / sieht / spricht
- **Beweis:** `python -m src.scripts.proof_hoert_sieht_spricht` → Report in `data/proof_hoert_sieht_spricht_report.txt`.
- **Status:** [ATLAS_HOERT_SIEHT_SPRICHT_STATUS.md](ATLAS_HOERT_SIEHT_SPRICHT_STATUS.md) – was fehlt, was bewiesen.

## Nächste Prioritäten
- Hören: Pipeline Scout-Mikro/Assist → ATLAS. Sehen: go2rtc/CAMERA_SNAPSHOT_URL. Scout live: User fügt Doku in HA ein.

---
**Wenn du wieder da bist:** [WIEDER_DA_ALLES_LAEUFT.md](WIEDER_DA_ALLES_LAEUFT.md) – Checkliste + Start-Skripte.

**Vollständig:** ATLAS_ZWISCHENZIELE.md, ATLAS_PROTOTYP_STATUS_0.5.md, ATLAS_SCHNITTSTELLEN_UND_KANAALE.md, ORCHESTRATOR_STRATEGY.md.
