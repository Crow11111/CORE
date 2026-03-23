import sys
import os
import requests
import tempfile
import subprocess
import signal
import time

# OMEGA-Kontext
API_BASE = os.getenv("CORE_API_URL", "http://127.0.0.1:8000")
TEMP_DIR = tempfile.gettempdir()
PID_FILE = os.path.join(TEMP_DIR, "core_dictate.pid")
WAV_FILE = os.path.join(TEMP_DIR, "core_dictate.wav")

# Razer Seiren V3 Mini Node-Name
MIC_TARGET = "alsa_input.usb-Razer_Inc._Razer_Seiren_V3_Mini-00.pro-input-0"

def show_notification(text, urgency="normal"):
    subprocess.run(["notify-send", "-t", "3000", "-u", urgency, "CORE Input", text])

def check_audio_level(file_path):
    """Prüft die durchschnittliche Lautstärke (RMS-ähnlich) via ffmpeg."""
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
            return -91.0, -91.0

        cmd = ["ffmpeg", "-i", file_path, "-af", "volumedetect", "-f", "null", "/dev/null"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        max_vol = -91.0
        mean_vol = -91.0

        for line in res.stderr.splitlines():
            if "max_volume" in line:
                max_vol = float(line.split(":")[-1].replace("dB", "").strip())
            if "mean_volume" in line:
                mean_vol = float(line.split(":")[-1].replace("dB", "").strip())

        return max_vol, mean_vol
    except Exception as e:
        print(f"Level check error: {e}")
    return -91.0, -91.0

def copy_to_clipboard(text):
    try:
        process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
    except FileNotFoundError:
        try:
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(input=text.encode('utf-8'))
        except FileNotFoundError:
            pass

def start_recording(mode="deep"):
    if os.path.exists(PID_FILE):
        show_notification("Aufnahme läuft bereits!", "critical")
        return

    # Nativer Pipewire Record (pw-record)
    # --format=s16, --rate=16000, --channels=1
    # WAV-Header wird automatisch gesetzt
    # Target: Razer Seiren V3 Mini
    try:
        # Wir setzen XDG_RUNTIME_DIR sicherheitshalber explizit, falls aus System-Kontext gestartet
        env = os.environ.copy()
        if "XDG_RUNTIME_DIR" not in env:
            env["XDG_RUNTIME_DIR"] = "/run/user/1000"

        proc = subprocess.Popen([
            "pw-record",
            "--target", MIC_TARGET,
            "--format", "s16",
            "--rate", "16000",
            "--channels", "1",
            WAV_FILE
        ], env=env)
    except FileNotFoundError:
        # Fallback auf arecord falls pw-record fehlt (unwahrscheinlich auf CachyOS)
        proc = subprocess.Popen(["arecord", "-D", "pulse", "-f", "S16_LE", "-c", "1", "-r", "16000", WAV_FILE])

    time.sleep(0.3)
    if proc.poll() is not None:
        show_notification(f"Fehler: pw-record konnte nicht starten. (Target: {MIC_TARGET})", "critical")
        return

    with open(PID_FILE, "w") as f:
        f.write(f"{proc.pid}:{mode}")

    show_notification(f"🔴 Aufnahme AKTIV ({mode})")

def stop_recording():
    if not os.path.exists(PID_FILE):
        return

    with open(PID_FILE, "r") as f:
        data = f.read().strip()
        pid, mode = data.split(":")
        pid = int(pid)

    try:
        os.kill(pid, signal.SIGTERM)
        # Warten bis Pipewire das File sauber schließt
        for _ in range(20):
            if not os.path.exists(f"/proc/{pid}"):
                break
            time.sleep(0.1)
    except ProcessLookupError:
        pass

    os.remove(PID_FILE)

    # Robustes Warten: Stelle sicher, dass die Datei fertig geschrieben ist.
    time.sleep(0.2) # Kurze initiale Pause
    try:
        initial_size = os.path.getsize(WAV_FILE)
        time.sleep(0.2)
        if os.path.getsize(WAV_FILE) != initial_size:
             time.sleep(0.3) # Gib dem Prozess mehr Zeit
    except FileNotFoundError:
        show_notification("❌ Aufnahmedatei nicht gefunden.", "critical")
        return

    max_vol, mean_vol = check_audio_level(WAV_FILE)
    if mean_vol < -55.0:
        show_notification(f"❌ KEIN SIGNAL (Mean: {mean_vol} dB).", "critical")
        if os.path.exists(WAV_FILE): os.remove(WAV_FILE)
        return

    show_notification(f"⌛ Transkribiere (Mean: {mean_vol} dB)...")

    try:
        with open(WAV_FILE, "rb") as f:
            urls = [API_BASE, "http://127.0.0.1:8000", "http://localhost:8000"]
            success = False
            for base in urls:
                try:
                    url = f"{base.rstrip('/')}/api/dictate"
                    if mode == "live":
                        url += "?mode=live"

                    f.seek(0) # WICHTIG: Dateizeiger für jeden Versuch zurücksetzen
                    files = {"audio": ("dictate.wav", f, "audio/wav")}
                    resp = requests.post(url, files=files, timeout=60)

                    if resp.status_code == 200:
                        text = resp.json().get("text", "").strip()
                        if text:
                            copy_to_clipboard(text)
                            show_notification(f"✅ In Zwischenablage.", "normal")
                        else:
                            show_notification("ℹ️ Kein Text erkannt.", "normal")
                        success = True
                        break
                except Exception:
                    continue

            if not success:
                show_notification("❌ Backend nicht erreichbar.", "critical")

    except Exception as e:
        show_notification(f"❌ API Fehler: {str(e)}", "critical")
    finally:
        if os.path.exists(WAV_FILE):
            os.remove(WAV_FILE)

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "stop"
    mode = sys.argv[2] if len(sys.argv) > 2 else "deep"

    if action == "start":
        start_recording(mode)
    elif action == "stop":
        stop_recording()
    elif action == "toggle":
        if os.path.exists(PID_FILE):
            stop_recording()
        else:
            start_recording(mode)
