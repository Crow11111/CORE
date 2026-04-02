# SESSION LOG 2026-04-02: TTS Timeout & Stream Fix

## 1. Initiale Analyse
- **Problem**: `python src/scripts/omega_vision_test.py` rannte beim Dispatch der TTS in einen Timeout (`read timeout=20`). Der HA Mini startete kurz, spielte aber keinen Ton.
- **Root Cause**: In `src/voice/tts_dispatcher.py` startete die Funktion `_stream_audio_to_mini` einen blockierenden, temporären `HTTPServer` (Port 8002) in einem Thread und blockierte den Caller via `asyncio.sleep(8)`. Dadurch überstieg die Gesamtdauer (LLM/TTS Generierung + 8s Sleep) die 20s Timeout-Schwelle von `requests.post`. Außerdem führte das sofortige Shutdown des Servers in manchen Fällen dazu, dass HA Mini die Datei nicht vollständig laden konnte.

## 2. Deliverables & Anpassungen
- **FastAPI Media Mount**: `src/api/main.py` erweitert. Das Verzeichnis `/OMEGA_CORE/media/` wird nun dauerhaft statisch unter der Route `/media/` auf Port 8000 serviert.
- **Non-blocking Stream**: In `src/voice/tts_dispatcher.py` wurde der unzuverlässige Thread-HTTP-Server entfernt. Stattdessen konstruieren `_stream_audio_to_mini` und `_elevenlabs_stream_to_mini` die Audio-URL nun nativ über `http://CORE_HOST_IP:CORE_API_PORT/media/...` und senden den `play_media` Befehl ab, woraufhin die Funktion ohne Blockade zurückkehrt.
- **Refactoring**: Die redundante Stream-Server-Logik aus `_elevenlabs_stream_to_mini` wurde komplett entfernt und die Funktion leitet nun den Dateipfad sauber in den optimierten `_stream_audio_to_mini` weiter.

## 3. Test & Validierung
- **Manueller API Test**: Ein asynchroner Dispatch via `curl` an `/api/core/dispatch-tts` kehrte instantan zurück (response time < 100ms nach Audio-Erstellung).
- **Log Verification**: Backend-Logs zeigten die erfolgreiche Zustellung und HA Mini konnte das Audio nahtlos via `GET /media/...` laden und abspielen.
- **Axiom Compliance**: Keine `0.5` oder Dummy-Werte. Der Stream wurde robuster, transparenter und blockiert nicht den asynchronen Ablauf.

## Status
Abnahme erteilt. System ist robust und der Timeout Fehler behoben.

[LEGACY_UNAUDITED]
