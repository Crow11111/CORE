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
    # OMEGA Gruppe JID
    target = "120363425156111771@g.us"
    text = "*(DEBUG TEST)* - Evolution API Outbound Group Check. Wenn ich das hier in der Gruppe posten kann, bin ich definitiv 'drin'. Inbound (Hören) wird noch korrigiert."

    print(f"Sende Nachricht an Gruppe {target}...")
    success = await client.send_whatsapp_async(target, text)

    if success:
        print("Gruppen-Nachricht erfolgreich gesendet!")
    else:
        print("Fehler beim Senden an die Gruppe.")

if __name__ == "__main__":
    asyncio.run(main())
