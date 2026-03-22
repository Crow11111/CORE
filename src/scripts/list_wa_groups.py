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
    endpoint = f"{url}/group/fetchAllGroups/{instance}?getParticipants=false"

    print(f"Abfrage der Gruppen von: {endpoint}")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(endpoint, headers=headers, timeout=20.0)
            if r.status_code == 200:
                groups = r.json()
                print(f"Gefundene Gruppen: {len(groups)}")
                for g in groups:
                    # In Evolution API v1 ist es oft eine Liste von Objekten mit 'id' und 'subject'
                    jid = g.get("id") or g.get("jid")
                    name = g.get("subject") or g.get("name")
                    print(f"- {name} (JID: {jid})")
            else:
                print(f"Fehler {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
