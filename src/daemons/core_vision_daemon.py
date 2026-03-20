# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Vision Daemon (The All-Seeing Eye)
----------------------------------------
go2rtc HTTP-Snapshot Edition — kein cv2/RTSP noetig.

Holt JPEG-Snapshots via go2rtc HTTP API, vergleicht Frames
per Pixel-Differenz (PIL/numpy), schickt bei Symmetrie-Bruch
das Bild an Gemini Vision.

Env-Variablen:
  GO2RTC_BASE_URL  (default http://192.168.178.54:1984)
  GO2RTC_STREAM_NAME  (default mx_brio)
  GOOGLE_API_KEY / GEMINI_API_KEY
"""

import sys
import io
import time
import os
import threading
import asyncio
from dotenv import load_dotenv

try:
    import numpy as np
    from PIL import Image
except ImportError as _ie:
    print(f"[VISION] FATAL: {_ie}. Daemon beendet sich sauber.", flush=True)
    sys.exit(0)

try:
    import requests
except ImportError:
    print("[VISION] FATAL: requests nicht installiert. Daemon beendet sich sauber.", flush=True)
    sys.exit(0)

try:
    import google.generativeai as genai
except ImportError:
    print("[VISION] FATAL: google-generativeai nicht installiert. Daemon beendet sich sauber.", flush=True)
    sys.exit(0)

load_dotenv("/OMEGA_CORE/.env")

GO2RTC_BASE = os.getenv("GO2RTC_BASE_URL", "http://192.168.178.54:1984").rstrip("/")
STREAM_NAME = os.getenv("GO2RTC_STREAM_NAME", "mx_brio")
SNAPSHOT_URL = f"{GO2RTC_BASE}/api/frame.jpeg?src={STREAM_NAME}"

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3-flash"

PHI = 1.6180339887
SYMMETRY_BREAK_THRESHOLD = 12.0
COOLDOWN_SECONDS = 5 * PHI
POLL_INTERVAL = 2.0


def _fetch_snapshot() -> Image.Image | None:
    try:
        r = requests.get(SNAPSHOT_URL, timeout=5)
        if r.status_code != 200:
            return None
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception as e:
        print(f"[VISION] Snapshot-Fehler: {e}")
        return None


def _frame_diff(a: Image.Image, b: Image.Image) -> float:
    """Mittlere absolute Pixel-Differenz (0-255 Skala)."""
    size = (320, 240)
    a_arr = np.asarray(a.resize(size), dtype=np.float32)
    b_arr = np.asarray(b.resize(size), dtype=np.float32)
    return float(np.mean(np.abs(a_arr - b_arr)))


class MthoVisionDaemon:
    def __init__(self):
        self.running = False
        self.last_observation_time = 0.0
        self.model = None
        self._setup_gemini()

    def _setup_gemini(self):
        if not GEMINI_API_KEY:
            print("[CRITICAL] GOOGLE_API_KEY fehlt in .env")
            return
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)
        print(f"[INIT] Gemini {MODEL_NAME} bereit.")

    def _analyze_frame(self, img: Image.Image):
        if self.model is None:
            return
        try:
            prompt = (
                "CORE SYSTEM MESSAGE: Describe what you see in this security feed. "
                "Focus on movement, changes, or anomalies. Be extremely concise (1 sentence). "
                "If nothing important is happening, say 'No significant entropy'."
            )
            t0 = time.time()
            response = self.model.generate_content([prompt, img])
            duration = time.time() - t0
            text = response.text.strip()
            print(f"[VISION] Gemini ({duration:.2f}s): {text}")

            if "No significant entropy" not in text:
                self._persist_and_notify(text, duration, img=img)
        except Exception as e:
            print(f"[ERROR] Vision API: {e}")

    def _persist_and_notify(self, text: str, duration: float, img: Image.Image = None):
        try:
            import hashlib, tempfile
            h = hashlib.md5(text[:50].encode()).hexdigest()[:10]
            doc_id = f"vision_{h}"
            document = f"[VISION] {text}"
            meta = {"duration_sec": round(duration, 2), "model": MODEL_NAME, "source": "vision_daemon"}

            if img is not None:
                tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                img.save(tmp, format="JPEG", quality=85)
                tmp.close()
                try:
                    from src.db.multi_view_client import ingest_multimodal
                    asyncio.run(ingest_multimodal(
                        document=document,
                        file_path=tmp.name,
                        mime_type="image/jpeg",
                        doc_id=doc_id,
                        source_collection="vision_observations",
                        metadata=meta,
                    ))
                    print("[VISION] Multimodal persist OK (Text + Bild-Vektor)")
                finally:
                    try:
                        os.unlink(tmp.name)
                    except OSError:
                        pass
            else:
                from src.db.multi_view_client import ingest_document
                asyncio.run(ingest_document(
                    document=document,
                    doc_id=doc_id,
                    source_collection="vision_observations",
                    metadata=meta,
                ))
        except Exception as e:
            print(f"[VISION] Persist fehlgeschlagen: {e}")

        self._forward_to_oc_brain(text, duration)
        self._try_tts(text)

    def _forward_to_oc_brain(self, analysis: str, duration: float):
        def _do():
            try:
                from src.network.openclaw_client import send_event_to_oc_brain
                ok, resp = send_event_to_oc_brain(
                    event_type="VISION_ALERT",
                    data={"analysis": analysis, "duration_sec": round(duration, 2), "model": MODEL_NAME, "source": "vision_daemon"},
                    timeout=10.0,
                )
                if ok:
                    print(f"[OC-BRAIN] Vision forwarded: {resp[:60]}...")
                else:
                    print(f"[OC-BRAIN] Forward failed: {resp}")
            except Exception as e:
                print(f"[OC-BRAIN] {e}")
        threading.Thread(target=_do, daemon=True).start()

    def _try_tts(self, analysis: str):
        keywords = ["person", "motion", "movement", "someone", "intruder"]
        if not any(kw in analysis.lower() for kw in keywords):
            return
        try:
            from src.agents.core_agent import IntentType, get_ephemeral_pool
            from src.agents.scout_core_handlers import register_all_handlers
            pool = get_ephemeral_pool()
            if not pool._handlers:
                register_all_handlers(pool)
            asyncio.run(pool.spawn_and_execute(
                IntentType.TTS_DISPATCH,
                {"text": f"Achtung: {analysis[:100]}", "target": "mini"},
                ttl=15.0,
            ))
        except Exception as e:
            print(f"[VISION-TTS] {e}")

    def run(self):
        print(f"[START] Vision via go2rtc: {SNAPSHOT_URL}")

        prev_frame = _fetch_snapshot()
        if prev_frame is None:
            print("[ERROR] go2rtc nicht erreichbar oder Stream offline. Warte 30s und versuche erneut...")
            time.sleep(30)
            prev_frame = _fetch_snapshot()
            if prev_frame is None:
                print("[FATAL] go2rtc nach Retry unerreichbar. Daemon beendet sich.")
                return

        self.running = True
        print("[RUN] Vision Loop aktiv. Warte auf Symmetrie-Bruch...")

        while self.running:
            time.sleep(POLL_INTERVAL)

            cur_frame = _fetch_snapshot()
            if cur_frame is None:
                continue

            diff = _frame_diff(prev_frame, cur_frame)
            now = time.time()

            if diff > SYMMETRY_BREAK_THRESHOLD:
                elapsed = now - self.last_observation_time
                if elapsed > COOLDOWN_SECONDS:
                    print(f"[EVENT] Bewegung (diff={diff:.1f} > {SYMMETRY_BREAK_THRESHOLD}). Analyse...")
                    threading.Thread(target=self._analyze_frame, args=(cur_frame.copy(),), daemon=True).start()
                    self.last_observation_time = now

            prev_frame = cur_frame


if __name__ == "__main__":
    daemon = MthoVisionDaemon()
    daemon.run()
