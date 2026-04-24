import asyncio
import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from src.connectors.home_assistant import HomeAssistantClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("Timer gestartet: 5 Minuten...")
    await asyncio.sleep(300)

    try:
        client = HomeAssistantClient()
        player = os.getenv("DEFAULT_MEDIA_PLAYER", "media_player.schreibtisch")
        print(f"Sende Sprachnachricht an {player}...")
        await client.speak(player, "Die fünf Minuten sind um. Prüfe die Pizza.", cache=False)
        print("Nachricht gesendet.")
    except Exception as e:
        print(f"Fehler beim Senden: {e}")

if __name__ == "__main__":
    asyncio.run(main())
