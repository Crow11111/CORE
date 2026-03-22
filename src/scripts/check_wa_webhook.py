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
    raw_instance = os.getenv("EVOLUTION_INSTANCE", "Marc ten Hoevel")
    instance = urllib.parse.quote(raw_instance)

    headers = {"apikey": apikey}
    endpoint = f"{url}/webhook/find/{instance}"

    print(f"Abfrage der Webhook-Konfiguration von: {endpoint}")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(endpoint, headers=headers, timeout=10.0)
            if r.status_code == 200:
                config = r.json()
                print("Aktuelle Webhook-Konfiguration:")
                print(json.dumps(config, indent=2))
            else:
                print(f"Fehler {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    import json
    asyncio.run(main())
