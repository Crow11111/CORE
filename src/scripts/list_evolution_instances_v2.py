import os, httpx, json, urllib.parse
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

url = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
apikey = os.getenv("EVOLUTION_API_KEY", "")

if not url or not apikey:
    print("Fehler: EVOLUTION_API_URL oder _KEY fehlen in .env")
    exit(1)

async def check_instances():
    async with httpx.AsyncClient() as client:
        headers = {"apikey": apikey}
        # V2 Endpoint zum Listen aller Instanzen
        r = await client.get(f"{url}/instance/fetchInstances", headers=headers)
        print(f"Status fetchInstances: {r.status_code}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print(r.text)

import asyncio
asyncio.run(check_instances())
