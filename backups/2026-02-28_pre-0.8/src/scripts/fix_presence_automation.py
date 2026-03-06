import os
import httpx
import asyncio
import urllib3
from loguru import logger
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

HASS_URL = os.getenv("HA_URL")
HASS_TOKEN = os.getenv("HA_TOKEN")

if not HASS_URL:
    HASS_URL = "http://192.168.178.54:8123" # Fallback from previous context

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json",
}

async def update_automation():
    # Updating the existing "Atlas Presence Director" automation
    # We use the same ID 'atlas_presence_director' to overwrite it.
    automation_id = "atlas_presence_director" 
    url = f"{HASS_URL}/api/config/automation/config/{automation_id}"

    # New simplified logic using DIRECT SENSORS (iPhone) instead of complex Bayesian
    automation_config = {
        "alias": "System: ATLAS Presence Director (Direct Mode)",
        "description": "Robuste Präsenzsteuerung direkt über iPhone Tracking (Fallback für fehlenden Bayesian Sensor). Schaltet mth91/mth_away.",
        "mode": "restart",
        "trigger": [
            # Trigger: iPhone kommt nach Hause
            {
                "platform": "state",
                "entity_id": "device_tracker.iphone_2",
                "to": "home",
                "id": "mth_arrives"
            },
            # Trigger: iPhone verlässt Zuhause (mit Puffer gegen GPS-Sprünge)
            {
                "platform": "state",
                "entity_id": "device_tracker.iphone_2",
                "from": "home",
                "to": "not_home",
                "for": "00:05:00",
                "id": "mth_leaves"
            }
        ],
        "condition": [],
        "action": [
            {
                "choose": [
                    # Aktion: Ankommen
                    {
                        "conditions": [{"condition": "trigger", "id": "mth_arrives"}],
                        "sequence": [
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth_away"}},
                            {"service": "persistent_notification.create", "data": {"message": "ATLAS Presence: Welcome Home (iPhone)", "title": "Presence Log"}}
                        ]
                    },
                    # Aktion: Verlassen
                    {
                        "conditions": [{"condition": "trigger", "id": "mth_leaves"}],
                        "sequence": [
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth_away"}},
                            {"service": "persistent_notification.create", "data": {"message": "ATLAS Presence: Goodbye (iPhone)", "title": "Presence Log"}}
                        ]
                    }
                ]
            }
        ]
    }

    print(f"Updating automation {automation_id} at {url}...")
    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        try:
            r = await client.post(url, headers=HEADERS, json=automation_config)
            print(f"Status Code: {r.status_code}")
            if r.status_code in (200, 201):
                print("SUCCESS: Automation updated! It now uses iPhone directly.")
            else:
                print(f"FAILED: {r.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(update_automation())
