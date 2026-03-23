# ATLAS hört / sieht / spricht – Status (Teamchef)

**Stand:** Beweis-basiert. Nichts glauben, alles prüfen.

---

## Ziele (vorgegeben)

| Ziel | Beweiskriterium |
|------|------------------|
| **ATLAS hört** | Aufzeichnung/Transkript von Scout-Mikro oder Dreadnought erreicht ATLAS/OC; reproduzierbar. |
| **ATLAS sieht** | Bild/Stream von Kamera (Scout oder MX/Brio) wird von ATLAS genutzt oder gespeichert; Pfad/Datei nachweisbar. |
| **ATLAS spricht** | TTS-Audio erreicht User (Boxen/WhatsApp/Abspielgerät); User hat es gehört oder Datei/Log beweist Ausgabe. |

---

## Ist-Zustand (geprüft)

### ATLAS hört – **[FAIL]** nicht umgesetzt

- **Scout:** Kein Pipeline Scout-Mikro → ATLAS/OC. HA Assist/Wyoming (Whisper, Piper) ist Doku ([usb_microphone_research.md](../03_INFRASTRUCTURE/usb_microphone_research.md)); kein Code in ATLAS, der Aufnahme oder Transkript von Scout abholt.
- **Dreadnought:** Kein Skript, das lokales Mikro aufzeichnet und an Event-Ingest/OC sendet.
- **Nächster Schritt:** Entweder (1) HA Voice Pipeline → Webhook mit Transkript an ATLAS/OC, oder (2) Skript auf Dreadnought: Aufnahme → Upload/Event. Beweis: Transkript oder Audio-Datei in Repo/OC.

### ATLAS sieht – **[TEIL]** nur Dreadnought/MX

- **Dreadnought (Brio/MX):** `mx_save_images_only.py` speichert Bilder in `data/mx_test/`, wenn go2rtc (localhost:1984) **oder** `camera_snapshot_server.py` + `CAMERA_SNAPSHOT_URL` laufen. Beweis: Dateien in `data/mx_test/`.
- **Scout:** Keine Aufzeichnung „auf dem Scout“ in ATLAS. Kamera auf Scout = HA (FFmpeg/MotionEye); ATLAS holt davon aktuell nichts. Nächster Schritt: HA-Kamera-Entity Snapshot-URL in .env, go2rtc_client erweitern oder Skript, das von HA-Snapshot-URL lädt und speichert.
- **Beweis Sehen:** `python -m src.scripts.mx_save_images_only` ausführen → mind. 1 Datei in `data/mx_test/` → Pfad protokollieren.

### ATLAS spricht – **[CODE OK, BEWEIS FEHLT]**

- **TTS:** `POST /api/atlas/tts`, `speak_text()`, `test_atlas_speak.py` → MP3 in `media/`. Code vorhanden.
- **User hat nichts gehört:** Kein Nachweis, dass Audio an Boxen oder WhatsApp gesendet wurde. `test_atlas_speak` sendet **Text** via HA-WhatsApp, nicht die TTS-Audio-Datei. `send_audio_to_whatsapp` sendet feste Datei (dev_agent_reply.mp3), braucht `ATLAS_HOST_IP` damit HA die Datei lädt.
- **Beweis Sprechen:** (1) TTS erzeugen, (2) dieselbe Datei per `send_audio_to_whatsapp` an WhatsApp (oder Abspielen lokal mit `play=True`). Verifikation: Datei existiert + optional WhatsApp-Nachricht/Log.

---

## Beweis-Skript

`python -m src.scripts.proof_hoert_sieht_spricht` führt aus:

1. **Sehen:** 1× Snapshot (MX/Brio oder CAMERA_SNAPSHOT_URL), speichert in `data/mx_test/`, schreibt Pfad in Log/Report.
2. **Sprechen:** TTS erzeugen → `media/`; optional: dieselbe Datei an WhatsApp senden (HA erreichbar, WHATSAPP_TARGET_ID).
3. **Hören:** Kein Code → Report: „[FAIL] Hören nicht umgesetzt; siehe ATLAS_HOERT_SIEHT_SPRICHT_STATUS.md“.

Report wird in `data/proof_hoert_sieht_spricht_report.txt` geschrieben (Exit-Codes, Pfade, Fehler).

---

## Nächste Aktionen (Teamchef)

| Priorität | Aktion | Verifikation |
|-----------|--------|--------------|
| 1 | `proof_hoert_sieht_spricht` ausführen | Report + Dateien prüfen |
| 2 | Sprechen: TTS-MP3 an WhatsApp senden (oder Play) | User hört Nachricht oder Log zeigt Erfolg |
| 3 | Sehen: MX-Snapshot einmal laufen lassen | `data/mx_test/*.jpg` existiert |
| 4 | Hören: Pipeline definieren (HA Webhook oder Dreadnought-Recording) | Transkript/Audio-Datei vorhanden |
| 5 | Scout-Kamera: HA-Snapshot-URL an ATLAS anbinden | Snapshot von Scout in data/ gespeichert |

---

**Referenz:** SCOUT_USB_KAMERA_MIKRO_HA_OS.md, usb_microphone_research.md, CAMERA_GO2RTC_WINDOWS.md, ha_client.send_whatsapp_audio.

---

## Letzter Proof-Lauf

**Datum:** 2026-02-28

`python -m src.scripts.proof_hoert_sieht_spricht` – Report in `data/proof_hoert_sieht_spricht_report.txt`.

| Ziel     | Ergebnis | Beweis |
|----------|----------|--------|
| Sehen    | FAIL     | HTTPConnectionPool localhost:1984 /api/frame.jpeg nicht erreichbar (Max retries exceeded) |
| Sprechen | OK       | media/proof_tts.mp3 + WhatsApp via HA gesendet |
| Hören    | FAIL     | Nicht umgesetzt (Scout-Mikro/Assist→ATLAS fehlt) |
