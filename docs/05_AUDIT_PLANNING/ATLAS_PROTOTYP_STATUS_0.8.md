# ATLAS Prototyp-Status 0.8

**Stand:** 28.02.2026 | **Phase:** Vollständige Sensorik-Pipeline (Prototyp 0.8)

---

## Was läuft (Beweis-Status: OK)

| Ziel | Komponente | Status | Beweis |
|------|------------|--------|--------|
| **Sprechen** | ElevenLabs TTS + HA-WhatsApp | **OK** | MP3 erzeugt + via WhatsApp gesendet (Beweis-Report) |
| **Sehen** | go2rtc + HA-Proxy-Fallback | **OK** | Snapshot via HA-Kamera (Balkon) gespeichert in `data/mx_test/` |
| **Hören** | Dreadnought Recording Pipeline | **OK** | `dreadnought_listen.py` sendet Audio-Event an OC Brain |
| OC Brain | OpenClaw VPS | **OK** | Antwortet auf Events (Z6, Z13, Z15) |
| Event-Ingest | FastAPI /api/atlas/event | **OK** | Speichert Events in `data/events/` |

---

## Erreichte Zwischenziele (Phase 23h Autonomie)

- **Z9:** Scout HA Doku korrigiert und verifiziert.
- **Z11:** Alle Voice-IDs in `voice_config.py` belegt (Fallback-Struktur).
- **Z13:** E2E Event→OC→TTS Pipeline erfolgreich durchlaufen.
- **Z15:** `fetch_oc_submissions` Skript bereit für Roundtrip.
- **Backup:** Universales Backup (`backups/2026-02-28_pre-0.8`) erstellt.

---

## Nächste Prioritäten (Richtung 1.0)

1. **Echtzeit-Hören:** Hardware-Support (`sounddevice`) auf dem Ziel-Host sicherstellen für echte Audio-Transkription.
2. **Computer Vision:** ATLAS soll die gesehenen Bilder analysieren (Vision-Modell im OC Brain Task-Loop).
3. **Autonome Steuerung:** HA-Entitäten direkt aus dem OC Brain steuern (über Spine).

---

## Letzter Proof-Lauf (Full Proof)

```bash
python -m src.scripts.proof_hoert_sieht_spricht
```

Report: `data/proof_hoert_sieht_spricht_report.txt`
- Sehen: OK (via Fallback)
- Sprechen: OK (TTS + WA)
- Hören: OK (Pipeline/Event)
