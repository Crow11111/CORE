import requests
import json
import time

def test_tts_bridge():
    url = "http://localhost:8000/v1/audio/speech"
    payload = {
        "input": "Hallo Operator, ich bin ATLAS. Meine Stimme ist nun konsistent und loyal.",
        "voice": "Kore"
    }

    print(f"Sende TTS-Request an {url}...")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=30)
        end_time = time.time()

        if response.status_code == 200:
            print(f"TTS-Request erfolgreich ({end_time - start_time:.2f}s).")
            print(f"Audio-Größe: {len(response.content)} Bytes.")

            # Speicher Test-Audio
            with open("/OMEGA_CORE/media/test_voice_fix.wav", "wb") as f:
                f.write(response.content)
            print("Audio gespeichert unter /OMEGA_CORE/media/test_voice_fix.wav.")
        else:
            print(f"Fehler: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Fehler beim Test: {e}")

if __name__ == "__main__":
    test_tts_bridge()
