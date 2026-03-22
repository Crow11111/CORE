import os, httpx, json, urllib.parse
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

url = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
apikey = os.getenv("EVOLUTION_API_KEY", "")
raw_instance = os.getenv("EVOLUTION_INSTANCE", "Marc ten Hoevel")
instance = urllib.parse.quote(raw_instance)

async def update_settings():
    async with httpx.AsyncClient() as client:
        headers = {"apikey": apikey}
        payload = {
            "rejectCall": False,
            "msgCall": "",
            "groupsIgnore": False,
            "alwaysOnline": True,
            "readMessages": False,  # DEAKTIVIERT gegen Loop-Verdacht
            "readStatus": False,
            "syncFullHistory": True
        }
        r = await client.post(f"{url}/settings/set/{instance}", headers=headers, json=payload)
        print(f"Status update settings: {r.status_code}")
        print(r.text)

import asyncio
asyncio.run(update_settings())
