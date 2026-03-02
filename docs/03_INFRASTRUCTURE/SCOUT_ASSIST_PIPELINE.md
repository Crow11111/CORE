# Scout Assist Pipeline: Voice-Eingabe (Headset-Mikro)
#
# Das Samsung USB-C Headset am Scout dient als Mikrofon-Eingabe für ATLAS.
# TTS-Ausgabe geht über die Google Minis (Schreibtisch, Regal etc.).
#
# ── Voraussetzung: 4 Addons in HA installieren ──
#
# Einstellungen → Add-ons → Add-on Store:
#
#   1. Whisper          → Speech-to-Text (lokal, kein Cloud)
#   2. Piper            → Text-to-Speech (lokal)
#   3. openWakeWord     → Wake-Word-Erkennung ("Hey Jarvis" etc.)
#   4. Assist Microphone → Bindet USB-Mikro als Audio-Input ein
#
# ── Assist Microphone konfigurieren ──
#
# Im Addon "Assist Microphone" → Konfiguration:
#
#   Audio Input:  alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback
#   Audio Output: media_player.schreibtisch (Google Mini am Schreibtisch)
#
#   NICHT das Headset als Speaker -- liegt oben auf dem PC, unhörbar.
#   Die Minis (Schreibtisch, Regal etc.) sind die Standard-Ausgabe.
#
# ── Voice Pipeline erstellen ──
#
# Einstellungen → Voice Assistants → Pipeline hinzufügen:
#
#   STT Engine:         Whisper
#   TTS Engine:         Piper
#   Wake Word Engine:   openWakeWord ("Hey Jarvis" oder custom)
#   Conversation Agent: Home Assistant (oder Ollama falls eingerichtet)
#
# ── Hardware-Zuordnung ──
#
#   | Device                  | PulseAudio ID                                                          | Zweck               |
#   |-------------------------|------------------------------------------------------------------------|----------------------|
#   | Samsung Headset (Mikro) | alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback          | Spracheingabe/Assist |
#   | Google Mini Schreibtisch| media_player.schreibtisch                                              | TTS-Ausgabe          |
#   | Brio Mikro              | alsa_input.usb-046d_Logitech_BRIO_657ACFE9-03.analog-stereo           | Raumüberwachung      |
#
# ── Parallel-Nutzung ──
#
# PulseAudio erlaubt mehrere Konsumenten auf einer Source.
# Das Headset-Mikro kann gleichzeitig von Assist UND go2rtc (headset_mic Stream) genutzt werden.
# Kein Konflikt.
#
# ── Test ──
#
# Nach Einrichtung: "Hey Jarvis" ins Headset sagen → HA sollte reagieren.
# Alternativ: In HA → Entwicklerwerkzeuge → Dienste → assist_pipeline.run aufrufen.
