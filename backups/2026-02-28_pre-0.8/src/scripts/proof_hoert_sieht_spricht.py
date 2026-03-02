"""
Beweis: ATLAS hört / sieht / spricht.
Führt prüfbare Schritte aus, schreibt Report nach data/proof_hoert_sieht_spricht_report.txt.
Teamchef: Nur Beweise zählen.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

REPORT_PATH = PROJECT_ROOT / "data" / "proof_hoert_sieht_spricht_report.txt"
MX_SAVE_DIR = Path(os.getenv("MX_SAVE_DIR", str(PROJECT_ROOT / "data" / "mx_test")))
MEDIA_DIR = PROJECT_ROOT / "media"


def log(msg: str, lines: list) -> None:
    lines.append(msg)
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def run_sehen(lines: list) -> tuple[bool, str]:
    """1 Snapshot, speichern in data/mx_test/. Return (ok, path_or_error)."""
    try:
        from src.network.go2rtc_client import get_snapshot, is_configured
        if not is_configured():
            return False, "GO2RTC/CAMERA_SNAPSHOT_URL nicht konfiguriert"
        MX_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        ok, data = get_snapshot(timeout=15.0)
        if not ok or not isinstance(data, bytes):
            return False, str(data)[:200]
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = MX_SAVE_DIR / f"proof_mx_{ts}.jpg"
        path.write_bytes(data)
        return True, str(path)
    except Exception as e:
        return False, str(e)[:200]


def run_sprechen(lines: list) -> tuple[bool, str]:
    """TTS erzeugen, in media/ speichern. Optional: an WhatsApp senden."""
    try:
        from src.voice.elevenlabs_tts import speak_text
        text = "ATLAS Proof. Hoeren, Sehen, Sprechen – Test."
        out_path = MEDIA_DIR / "proof_tts.mp3"
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = speak_text(
            text=text,
            role_name="atlas_dialog",
            output_path=str(out_path),
            play=False,
        )
        if not path or not os.path.isfile(path):
            return False, "TTS lieferte keine Datei"
        # Optional: an WhatsApp senden (wenn HA + Ziel konfiguriert)
        target = (os.getenv("WHATSAPP_TARGET_ID") or "").strip().strip('"').replace("@s.whatsapp.net", "")
        if target and os.getenv("HASS_URL") and os.getenv("HASS_TOKEN"):
            try:
                from src.network.ha_client import HAClient
                ok = HAClient().send_whatsapp_audio(to_number=target, audio_path=path)
                if ok:
                    return True, f"{path} + WhatsApp gesendet"
            except Exception as e:
                log(f"  WhatsApp optional FAIL: {e}", lines)
        return True, str(path)
    except Exception as e:
        return False, str(e)[:200]


def run_hoeren(lines: list) -> tuple[bool, str]:
    """Kein Pipeline – nur Dokumentation."""
    return False, "Nicht umgesetzt (Scout-Mikro/Assist->ATLAS fehlt)"


def main() -> int:
    lines = [f"Report {datetime.now(timezone.utc).isoformat()}"]
    log("--- Proof: ATLAS hört / sieht / spricht ---", lines)

    # Sehen
    log("\n[Sehen]", lines)
    ok_see, detail_see = run_sehen(lines)
    log(f"  {'OK' if ok_see else 'FAIL'}: {detail_see}", lines)

    # Sprechen
    log("\n[Sprechen]", lines)
    ok_speak, detail_speak = run_sprechen(lines)
    log(f"  {'OK' if ok_speak else 'FAIL'}: {detail_speak}", lines)

    # Hören
    log("\n[Hören]", lines)
    ok_hear, detail_hear = run_hoeren(lines)
    log(f"  {'OK' if ok_hear else 'FAIL'}: {detail_hear}", lines)

    # Report schreiben
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {REPORT_PATH}", lines)

    fails = sum(1 for o in [ok_see, ok_speak, ok_hear] if not o)
    return 2 if fails >= 2 else (1 if fails == 1 else 0)


if __name__ == "__main__":
    sys.exit(main())
