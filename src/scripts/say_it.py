"""
CLI-Skript zum Testen von TTS-Targets.

Usage:
    python -m src.scripts.say_it "Hallo Welt" --target gemini_tts
    python -m src.scripts.say_it "Test" --target mini
    python -m src.scripts.say_it "Test" --target elevenlabs
"""
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

import argparse
import asyncio
from dotenv import load_dotenv

load_dotenv()


async def main():
    parser = argparse.ArgumentParser(description="CORE TTS Test-Tool")
    parser.add_argument("text", help="Text zum Vorlesen")
    parser.add_argument("--target", default="gemini_tts", help="TTS-Target (gemini_tts, mini, elevenlabs, piper, ...)")
    parser.add_argument("--voice", default=None, help="Stimme (z.B. Kore, Puck, Charon)")
    parser.add_argument("--style", default=None, help="Stil-Anweisung (z.B. 'Sage freundlich:')")
    parser.add_argument("--no-play", action="store_true", help="Nicht abspielen, nur Datei erzeugen")
    args = parser.parse_args()

    if args.target == "gemini_tts" and args.voice:
        os.environ["GEMINI_TTS_VOICE"] = args.voice
    if args.target == "gemini_tts" and args.style:
        os.environ["GEMINI_TTS_STYLE"] = args.style

    from src.voice.tts_dispatcher import dispatch_tts
    ok = await dispatch_tts(args.text, target=args.target)
    print(f"Ergebnis: {'OK' if ok else 'FEHLGESCHLAGEN'}")


if __name__ == "__main__":
    asyncio.run(main())
