import os, sys, asyncio, httpx, uuid
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

BASE_URL = "http://localhost:8000"

async def test_group_wildcard():
    """Testet ob der neue Wildcard-Endpoint Gruppen-Nachrichten frisst."""
    print("\n--- [TEST WILDCARD] Group Upsert ---")
    trace_id = f"TEST-GROUP-{uuid.uuid4().hex[:4].upper()}"
    group_jid = "120363425156111771@g.us"

    # Simuliere Evolution V2 Event-spezifischen POST
    payload = {
        "event": "messages.upsert",
        "instance": "Marc ten Hoevel",
        "data": {
            "key": {
                "remoteJid": group_jid,
                "fromMe": False,
                "id": f"TEST-GRP-{uuid.uuid4().hex[:8]}"
            },
            "message": {
                "conversation": "@oc Status-Check in der Gruppe."
            },
            "messageTimestamp": 1678912345
        }
    }

    # Sende an /webhook/whatsapp/messages.upsert (Wildcard)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{BASE_URL}/webhook/whatsapp/messages.upsert", json=payload, timeout=5.0)
            print(f"Status Wildcard: {r.status_code}")
            print(f"Response: {r.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_group_wildcard())
