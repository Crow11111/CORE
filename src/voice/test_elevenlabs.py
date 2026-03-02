import os
import sys
from dotenv import load_dotenv

# Füge das Root-Verzeichnis zum Python-Path hinzu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.voice.elevenlabs_tts import speak_text

def test_generation():
    print("Testing ElevenLabs generation...")
    load_dotenv()
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found in .env")
        return

    text = "Hallo Marc. Dies ist ein Test der neuronalen Sprachausgabe."
    output = speak_text(text=text, role_name="atlas_dialog", play=False)
    
    if output and os.path.exists(output):
        print(f"SUCCESS: Audio generated at {output}")
    else:
        print("FAILURE: Audio generation failed.")

if __name__ == "__main__":
    test_generation()
