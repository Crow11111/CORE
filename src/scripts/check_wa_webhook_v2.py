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

async def check_webhook():
    async with httpx.AsyncClient() as client:
        headers = {"apikey": apikey}
        # V2 Endpoint zum Abfragen der Webhook-Config
        r = await client.get(f"{url}/webhook/find/{instance}", headers=headers)
        print(f"Status find webhook: {r.status_code}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print(r.text)

import asyncio
asyncio.run(check_webhook())
