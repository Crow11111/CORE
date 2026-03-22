import asyncio
import os
import sys

# Füge ROOT-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.network.evolution_client import EvolutionClient

async def main():
    print("Prüfe Evolution API Konfiguration...")
    client = EvolutionClient()

    if not client.is_configured():
        print("Fehler: EvolutionClient ist nicht korrekt in .env konfiguriert.")
        print(f"URL: {client.url}")
        print(f"KEY: {client.apikey[:5]}...")
        print(f"INSTANCE: {client.instance}")
        return

    print("Konfiguration OK!")

    # Optional: Ein Ping/Ping, um die Erreichbarkeit des VPS Servers zu prüfen.
    print(f"Ziel-URL: {client.url}/message/sendText/{client.instance}")
    print("Der Client ist bereit für Push/Pull via WhatsApp.")

if __name__ == "__main__":
    asyncio.run(main())
