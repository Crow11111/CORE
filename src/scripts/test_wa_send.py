import asyncio
import os
import sys

# Füge ROOT-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.network.evolution_client import EvolutionClient
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

async def main():
    client = EvolutionClient()
    target = os.getenv("WHATSAPP_TARGET_ID", "491788360264@s.whatsapp.net")
    text = "*(DEBUG TEST)* - Evolution API Outbound Check. Wenn du das siehst, funktioniert das Senden. Der Rückkanal (Webhooks) wird noch geprüft."

    print(f"Sende Nachricht an {target}...")
    success = await client.send_whatsapp_async(target, text)

    if success:
        print("Nachricht erfolgreich gesendet!")
    else:
        print("Fehler beim Senden der Nachricht.")

if __name__ == "__main__":
    asyncio.run(main())
