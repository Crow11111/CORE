import asyncio
import os
import sys
import httpx
import urllib.parse
from dotenv import load_dotenv

# Füge ROOT-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

load_dotenv("/OMEGA_CORE/.env")

async def main():
    url = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
    apikey = os.getenv("EVOLUTION_API_KEY", "")

    headers = {"apikey": apikey}
    # Häufiger Endpunkt für verfügbare Webhook-Events
    endpoint = f"{url}/webhook/events"

    print(f"Abfrage der verfügbaren Events von: {endpoint}")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(endpoint, headers=headers, timeout=10.0)
            if r.status_code == 200:
                events = r.json()
                print("Verfügbare Events:")
                print(json.dumps(events, indent=2))
            else:
                # Fallback: Versuche einen anderen Pfad oder schaue in die globale Konfig
                print(f"Fehler {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    import json
    asyncio.run(main())
