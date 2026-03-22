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

    # Die neue Tunnel-URL via Docker Gateway IP auf dem VPS
    webhook_url = "http://172.26.0.1:32777/webhook/whatsapp"
    secret = os.getenv("CORE_WEBHOOK_SECRET", "")

    headers = {
        "apikey": apikey,
        "Content-Type": "application/json"
    }

    # Alle unterstützten Events aus der Fehlermeldung
    events = [
        "MESSAGES_UPSERT", "MESSAGES_EDITED", "MESSAGES_UPDATE", "MESSAGES_DELETE",
        "SEND_MESSAGE", "CONTACTS_UPSERT", "CONTACTS_UPDATE", "GROUPS_UPSERT",
        "GROUP_UPDATE", "GROUP_PARTICIPANTS_UPDATE", "CONNECTION_UPDATE", "CALL"
    ]

    # Evolution API v1 webhook set payload
    payload = {
        "webhook": {
            "url": webhook_url,
            "enabled": True,
            "events": events,
            "headers": {
                "X-CORE-WEBHOOK-SECRET": secret
            }
        }
    }

    endpoint = f"{url}/webhook/set/{instance}"

    print(f"Setze Webhook-URL auf: {webhook_url}")
    print(f"Endpoint: {endpoint}")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(endpoint, headers=headers, json=payload, timeout=15.0)
            if r.status_code in (200, 201):
                print("Webhook erfolgreich aktualisiert!")
                print(r.json())
            else:
                print(f"Fehler {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
