import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

async def mass_toggle_kitchen():
    url = os.getenv("HASS_URL")
    token = os.getenv("HASS_TOKEN")

    # Alle gefundenen Küchen-Lichter
    entities = ["light.kuche", "light.led_kuche", "light.govee_light_2"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(verify=False) as client:
        print(f"--- MASS-TOGGLE KÜCHE ---")
        for eid in entities:
            print(f"Sende TOGGLE an {eid}...")
            try:
                resp = await client.post(
                    f"{url}/api/services/light/toggle",
                    headers=headers,
                    json={"entity_id": eid},
                    timeout=5.0
                )
                print(f"-> Resultat {eid}: {resp.status_code}")
            except Exception as e:
                print(f"-> FEHLER {eid}: {e}")

        # Prüfung nach 2 Sekunden
        await asyncio.sleep(2)
        print("\n--- STATUS-CHECK NACH TOGGLE ---")
        for eid in entities:
            try:
                resp = await client.get(f"{url}/api/states/{eid}", headers=headers)
                state = resp.json().get("state")
                print(f"- {eid}: {state}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(mass_toggle_kitchen())
