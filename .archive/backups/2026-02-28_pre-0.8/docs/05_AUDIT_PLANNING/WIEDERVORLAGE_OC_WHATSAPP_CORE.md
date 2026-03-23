# Wiedervorlage: WhatsApp Pairing + ATLAS-Weiterbau

**Angelegt:** 28.02.2026  

---

## ATLAS-Pipeline (ohne Warten auf WhatsApp)

- **Scout → OC Brain:** `send_event_to_oc_brain(event)` / `python -m src.scripts.scout_send_event_to_oc` (stdin JSON oder --type/--node/--device).
- **Event-Ingest API:** `POST /api/atlas/event` – Body: source, node_id, event_type, priority, data → speichert in `data/events/` + ChromaDB `events`.
- **OC Brain SOUL:** Event-Protokoll im Deploy (Eingabe = Scout-JSON → bestätigen, Logik laut ARCHITECTURE.md).
- **ChromaDB:** Collections `events`, `insights` in chroma_client; Events werden mit Metadata gespeichert.

WhatsApp später pairen, wenn Slot/Throttle es erlauben.

---

## 1. Bei Gelegenheit (WhatsApp)

- **WhatsApp erneut pairen:** Control-UI → Channels → WhatsApp. Slot ist frei (3/4 belegt).

---

## 2. ATLAS funktional weiterbauen

Ziel = **funktionales Tool** wie in ATLAS Neocortex V1.0 und Schnittstellen-Doc beschrieben:

- **Scout → OC Brain:** Webhook POST `/v1/responses` mit Event-JSON (source, node_id, event_type, data).
- **OC Brain:** Logik (Dreadnought-Status), ChromaDB/State, Eskalation per WhatsApp (`[ATLAS-ALERT]`).
- **Kanäle:** Dreadnought↔OC (bereits), rat_submissions (bereits), WhatsApp (nach Pairing), Scout-Webhook (Endpoint steht; Scout-Seite anbinden).

Konkret nach dem Pairing:

1. WhatsApp-Pairing verifizieren (Testnachricht an OC, Antwort prüfen).
2. Scout so konfigurieren, dass er bei relevanten Events POST an OC Brain sendet (Payload laut ATLAS_SCHNITTSTELLEN_UND_KANAALE.md).
3. Optional: ChromaDB-Collections `events`/`insights` auf VPS anlegen und in die Pipeline einhängen.

Referenz: `docs/02_ARCHITECTURE/ATLAS_NEOCORTEX_V1.md`, `docs/02_ARCHITECTURE/ATLAS_SCHNITTSTELLEN_UND_KANAALE.md`.
