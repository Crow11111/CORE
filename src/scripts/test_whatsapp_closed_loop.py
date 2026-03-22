import os, sys, asyncio, httpx, uuid, json
from dotenv import load_dotenv
from loguru import logger

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv("/OMEGA_CORE/.env")

BASE_URL = "http://localhost:8000"
OC_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
WA_TARGET = os.getenv("WHATSAPP_TARGET_ID", "491788360264@s.whatsapp.net")

async def test_pull_loop():
    """Testet den Pull-Kanal: WhatsApp -> OC -> WhatsApp."""
    print("\n--- [TEST PULL-LOOP] WhatsApp -> OC -> Response ---")
    trace_id = f"TEST-PULL-{uuid.uuid4().hex[:4].upper()}"
    
    # Mock WhatsApp Payload (Evolution API Format)
    # _normalize_whatsapp in entry_adapter expects a 'message' key at root
    payload = {
        "key": {
            "remoteJid": WA_TARGET,
            "fromMe": False,
            "id": f"TEST-{uuid.uuid4().hex[:8]}"
        },
        "message": {
            "conversation": "@oc Ping-Test für den geschlossenen Regelkreis."
        },
        "messageTimestamp": 1678912345
    }
    
    print(f"Sende Mock-WhatsApp (Trace: {trace_id})...")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{BASE_URL}/webhook/whatsapp", json=payload, timeout=10.0)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text}")
            
            if r.status_code == 200:
                data = r.json()
                print(f"Erfolg: {data.get('status')} | Trace: {data.get('trace_id')}")
            else:
                print("Fehler beim Senden des Webhooks.")
        except Exception as e:
            print(f"Exception: {e}")

async def test_push_loop():
    """Testet den Push-Kanal: OC -> WhatsApp."""
    print("\n--- [TEST PUSH-LOOP] OC -> WhatsApp ---")
    trace_id = f"TEST-PUSH-{uuid.uuid4().hex[:4].upper()}"
    
    # Mock OC Payload (rat_submission)
    payload = {
        "from": "oc_brain_test",
        "type": "rat_submission",
        "trace_id": trace_id,
        "payload": {
            "topic": "System-Status",
            "body": "Dies ist ein autonomer Push vom OC Brain (Closed-Loop-Test)."
        }
    }
    
    headers = {
        "X-API-Key": OC_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"Sende Mock-OC-Push (Trace: {trace_id})...")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{BASE_URL}/api/oc/webhook", json=payload, headers=headers, timeout=10.0)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text}")
            
            if r.status_code == 200:
                data = r.json()
                print(f"Erfolg: {data.get('ok')} | Trace: {data.get('trace_id')}")
            else:
                print("Fehler beim Senden des OC-Webhooks.")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    if not OC_TOKEN:
        print("Fehler: OPENCLAW_GATEWAY_TOKEN nicht in .env gefunden.")
        sys.exit(1)
        
    asyncio.run(test_pull_loop())
    # Wir warten kurz, damit der Background-Task im Backend Zeit hat
    import time
    time.sleep(2)
    asyncio.run(test_push_loop())
    print("\nTest abgeschlossen. Bitte CORE-Logs prüfen (Takt 1-4).")
