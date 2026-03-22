import os, httpx, json, urllib.parse
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

url = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
apikey = os.getenv("EVOLUTION_API_KEY", "")
raw_instance = os.getenv("EVOLUTION_INSTANCE", "Marc ten Hoevel")
instance = urllib.parse.quote(raw_instance)

if not url or not apikey:
    print("Fehler: EVOLUTION_API_URL oder _KEY fehlen in .env")
    exit(1)

async def check():
    async with httpx.AsyncClient() as client:
        # GET /instance/settings/{instance}
        headers = {"apikey": apikey}
        r = await client.get(f"{url}/instance/settings/{instance}", headers=headers)
        print(f"Status Settings: {r.status_code}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print(r.text)

        # GET /instance/connectionState/{instance}
        r = await client.get(f"{url}/instance/connectionState/{instance}", headers=headers)
        print(f"Status Connection: {r.status_code}")
        print(r.text)

import asyncio
asyncio.run(check())
