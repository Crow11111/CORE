import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

async def inventory_lights():
    url = os.getenv("HASS_URL")
    token = os.getenv("HASS_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(verify=False) as client:
        print(f"--- HA LICHT-INVENTUR ({url}) ---")
        try:
            resp = await client.get(f"{url}/api/states", headers=headers)
            resp.raise_for_status()
            states = resp.json()

            kitchen_lights = []
            for s in states:
                if s["entity_id"].startswith("light.") and ("kuche" in s["entity_id"] or "kueche" in s["entity_id"] or "küche" in s.get("attributes", {}).get("friendly_name", "").lower()):
                    kitchen_lights.append({
                        "id": s["entity_id"],
                        "name": s.get("attributes", {}).get("friendly_name"),
                        "state": s["state"]
                    })

            print(f"Gefundene Küchen-Lichter ({len(kitchen_lights)}):")
            for l in kitchen_lights:
                print(f"- {l['id']} ({l['name']}): {l['state']}")

        except Exception as e:
            print(f"FEHLER: {e}")

if __name__ == "__main__":
    asyncio.run(inventory_lights())
