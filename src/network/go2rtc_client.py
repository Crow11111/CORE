"""
Go2RTC-Client für ATLAS_CORE (Kamera am PC).
Läuft unter Windows aus driver/go2rtc_win64/; Standard-UI/API: http://localhost:1984.
Liest GO2RTC_BASE_URL und GO2RTC_STREAM_NAME aus .env.
Schnittstelle: Snapshot (Einzelbild) für Tests/Dashboard; Stream-URLs für HA/WebRTC.
"""
import os
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

GO2RTC_BASE_URL = os.getenv("GO2RTC_BASE_URL", "http://localhost:1984").rstrip("/")
GO2RTC_STREAM_NAME = os.getenv("GO2RTC_STREAM_NAME", "pc")
# Optional: On-Demand-Snapshot (z.B. camera_snapshot_server.py) – Webcam nur bei Abruf aktiv
CAMERA_SNAPSHOT_URL = os.getenv("CAMERA_SNAPSHOT_URL", "").strip()


def snapshot_url(stream_name: str = None) -> str:
    """URL für ein JPEG-Snapshot. Wenn CAMERA_SNAPSHOT_URL gesetzt: On-Demand-Webcam; sonst go2rtc."""
    if CAMERA_SNAPSHOT_URL:
        return CAMERA_SNAPSHOT_URL.rstrip("/").split("?")[0]
    name = stream_name or GO2RTC_STREAM_NAME
    return f"{GO2RTC_BASE_URL}/api/frame.jpeg?src={name}"


def get_snapshot(stream_name: str = None, timeout: float = 10.0) -> tuple[bool, bytes | str]:
    """
    Holt ein JPEG-Snapshot: bevorzugt CAMERA_SNAPSHOT_URL (On-Demand), sonst go2rtc.
    Returns: (success, jpeg_bytes oder Fehlermeldung)
    """
    url = snapshot_url(stream_name)
    try:
        import requests
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.content
        if not data or len(data) < 100:
            return False, "Leere oder zu kleine Antwort"
        # Kurz prüfen, ob es wie JPEG aussieht
        if data[:2] != b"\xff\xd8":
            return False, "Antwort ist kein JPEG"
        return True, data
    except Exception as e:
        return False, str(e)


def is_configured() -> bool:
    """True, wenn eine Snapshot-Quelle konfiguriert ist (go2rtc oder CAMERA_SNAPSHOT_URL)."""
    return bool(CAMERA_SNAPSHOT_URL) or bool(GO2RTC_BASE_URL and GO2RTC_STREAM_NAME)


def streams_api_url() -> str:
    """URL der go2rtc API-Streams-Liste (z. B. für Auflistung verfügbarer Streams)."""
    return f"{GO2RTC_BASE_URL}/api/streams"
