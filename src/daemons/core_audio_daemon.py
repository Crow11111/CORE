# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Audio Daemon — Raumklang via go2rtc + lokales Whisper
-----------------------------------------------------------
Stufe 1 (Standard):  faster-whisper auf Dreadnought (CPU/GPU, kostenlos)
Stufe 2 (Eskalation): Gemini 2.5 Flash nur bei kritischen Events

Holt Audio vom Brio-Mikrofon (go2rtc RTSP), transkribiert lokal,
erkennt Schluesselwoerter, eskaliert bei Bedarf an Gemini.

Env-Variablen:
  GO2RTC_BASE_URL, GO2RTC_STREAM_NAME
  AUDIO_CLIP_SECONDS  (default 8)
  AUDIO_SILENCE_THRESHOLD  (default 150, RMS)
  AUDIO_INJECT_CURSOR  (0/1, default 0)
  WHISPER_MODEL  (default small)
  WHISPER_DEVICE  (default cpu)
"""

import sys
import os
import time
import tempfile
import subprocess
import hashlib
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
load_dotenv("/OMEGA_CORE/.env")

try:
    import numpy as np
except ImportError:
    print("[AUDIO] FATAL: numpy fehlt.", flush=True)
    sys.exit(0)

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("[AUDIO] FATAL: faster-whisper fehlt. pip install faster-whisper", flush=True)
    sys.exit(0)

GO2RTC_BASE = os.getenv("GO2RTC_BASE_URL", "http://192.168.178.54:1984").rstrip("/")
STREAM_NAME = os.getenv("GO2RTC_STREAM_NAME", "mx_brio")

CLIP_SECONDS = int(os.getenv("AUDIO_CLIP_SECONDS", "8"))
SILENCE_RMS_THRESHOLD = int(os.getenv("AUDIO_SILENCE_THRESHOLD", "150"))
INJECT_CURSOR = os.getenv("AUDIO_INJECT_CURSOR", "0") == "1"

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE = "int8" if WHISPER_DEVICE == "cpu" else "float16"

ESCALATION_KEYWORDS = [
    "hilfe", "alarm", "feuer", "notfall", "einbrecher", "achtung",
    "polizei", "krankenwagen", "core", "omega", "hey core",
]

PHI = 1.6180339887
COOLDOWN = 3 * PHI


def _capture_audio_clip(duration: int = CLIP_SECONDS) -> str | None:
    """Holt Audio-Clip von go2rtc via ffmpeg, gibt Pfad zurück."""
    host = GO2RTC_BASE.split("//")[1].split(":")[0] if "//" in GO2RTC_BASE else "192.168.178.54"
    rtsp_url = f"rtsp://{host}:8554/{STREAM_NAME}"

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        cmd = [
            "ffmpeg", "-y",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-t", str(duration),
            tmp_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=duration + 15)
        if r.returncode != 0:
            os.unlink(tmp_path)
            return None
        if os.path.getsize(tmp_path) < 1000:
            os.unlink(tmp_path)
            return None
        return tmp_path
    except Exception as e:
        print(f"[AUDIO] Capture Fehler: {e}")
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        return None


def _is_silence(wav_path: str) -> bool:
    with open(wav_path, "rb") as f:
        wav = f.read()
    raw = wav[44:]
    if len(raw) < 100:
        return True
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    rms = float(np.sqrt(np.mean(samples ** 2)))
    return rms < SILENCE_RMS_THRESHOLD


def _inject_to_cursor(text: str):
    try:
        subprocess.run(
            ["ydotool", "type", "--clearmodifiers", "--", text],
            timeout=5,
        )
        print(f"[AUDIO] Cursor-Injection: {text[:60]}...")
    except Exception as e:
        print(f"[AUDIO] ydotool Fehler: {e}")


def _needs_escalation(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in ESCALATION_KEYWORDS)


class CoreAudioDaemon:
    def __init__(self):
        self.whisper: WhisperModel | None = None
        self.last_analysis_time = 0.0
        self._load_whisper()

    def _load_whisper(self):
        print(f"[AUDIO] Lade Whisper {WHISPER_MODEL_SIZE} ({WHISPER_DEVICE}/{WHISPER_COMPUTE})...")
        t0 = time.time()
        self.whisper = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE,
        )
        print(f"[AUDIO] Whisper geladen in {time.time()-t0:.1f}s")

    def _transcribe_local(self, wav_path: str) -> str:
        """Lokale STT via faster-whisper (kein API-Call)."""
        try:
            t0 = time.time()
            segments, info = self.whisper.transcribe(wav_path, language="de")
            text = " ".join([s.text.strip() for s in segments]).strip()
            dur = time.time() - t0
            if text:
                print(f"[AUDIO] Whisper ({dur:.2f}s): {text[:120]}")
            return text
        except Exception as e:
            print(f"[AUDIO] Whisper Fehler: {e}")
            return ""

    def _escalate_to_gemini(self, wav_path: str, local_text: str) -> str | None:
        """Eskalation an Gemini nur bei kritischen Events."""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                return None
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            audio_file = genai.upload_file(wav_path, mime_type="audio/wav")

            prompt = (
                f"CORE AUDIO ESKALATION. Lokale Transkription: '{local_text}'\n"
                "Analysiere den Audio-Clip tiefergehend:\n"
                "1. Korrigiere/erweitere die Transkription falls nötig\n"
                "2. Beschreibe relevante Geräusche (Alarm, Türklingel, Schreie, etc.)\n"
                "3. Bewerte die Dringlichkeit (NORMAL/WARNUNG/KRITISCH)\n"
                "Kurz und präzise auf Deutsch."
            )

            t0 = time.time()
            response = model.generate_content([prompt, audio_file])
            dur = time.time() - t0
            text = response.text.strip()

            try:
                genai.delete_file(audio_file.name)
            except Exception:
                pass

            print(f"[AUDIO] Gemini-Eskalation ({dur:.2f}s): {text[:120]}")
            return text
        except Exception as e:
            print(f"[AUDIO] Gemini-Eskalation Fehler: {e}")
            return None

    def _persist(self, text: str, wav_path: str = None, source: str = "whisper", escalation: str | None = None):
        """Speichert die Transkription. Nur bei Eskalation in die Vektor-DB (API), sonst nur lokal."""
        try:
            # Wenn keine Eskalation vorliegt, nur lokal loggen (Gedankenstream)
            if not escalation:
                log_file = "/OMEGA_CORE/logs/gedankenstream.log"
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{ts}] {text}\n")
                return

            h = hashlib.md5(text[:50].encode()).hexdigest()[:10]
            doc_id = f"audio_{h}"

            document = f"[AUDIO/{source.upper()}] {text}"
            if escalation:
                document += f"\n[ESKALATION] {escalation}"

            meta = {
                "source": f"audio_daemon/{source}",
                "escalated": str(bool(escalation)),
            }

            if wav_path and os.path.isfile(wav_path):
                from src.db.multi_view_client import ingest_multimodal
                asyncio.run(ingest_multimodal(
                    document=document,
                    file_path=wav_path,
                    mime_type="audio/wav",
                    doc_id=doc_id,
                    source_collection="audio_speech" if text else "audio_observations",
                    metadata=meta,
                ))
                print(f"[AUDIO] Multimodal persist OK (Text + Audio-Vektor)")
            else:
                from src.db.multi_view_client import ingest_document
                asyncio.run(ingest_document(
                    document=document,
                    doc_id=doc_id,
                    source_collection="audio_speech" if text else "audio_observations",
                    metadata=meta,
                ))
        except Exception as e:
            print(f"[AUDIO] Persist Fehler: {e}")

    def run(self):
        print(f"[AUDIO] Start — Stream: {STREAM_NAME}, Clip: {CLIP_SECONDS}s, RMS-Threshold: {SILENCE_RMS_THRESHOLD}")
        print(f"[AUDIO] STT: Whisper {WHISPER_MODEL_SIZE} lokal | Eskalation: Gemini (nur bei Keywords)")
        print(f"[AUDIO] Cursor-Injection: {'AN' if INJECT_CURSOR else 'AUS'}")

        while True:
            wav_path = _capture_audio_clip()
            if wav_path is None:
                print("[AUDIO] Kein Audio. Warte 10s...")
                time.sleep(10)
                continue

            try:
                if _is_silence(wav_path):
                    time.sleep(COOLDOWN)
                    continue

                now = time.time()
                if now - self.last_analysis_time < COOLDOWN:
                    time.sleep(COOLDOWN - (now - self.last_analysis_time))
                    continue

                text = self._transcribe_local(wav_path)
                self.last_analysis_time = time.time()

                if not text:
                    time.sleep(COOLDOWN)
                    continue

                escalation = None
                if _needs_escalation(text):
                    print(f"[AUDIO] ESKALATION getriggert: '{text[:60]}'")
                    escalation = self._escalate_to_gemini(wav_path, text)

                self._persist(text, wav_path=wav_path, source="whisper", escalation=escalation)

                if INJECT_CURSOR and text:
                    _inject_to_cursor(text)

            finally:
                try:
                    os.unlink(wav_path)
                except OSError:
                    pass

            time.sleep(COOLDOWN)


if __name__ == "__main__":
    daemon = CoreAudioDaemon()
    daemon.run()
