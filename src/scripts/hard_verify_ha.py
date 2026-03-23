import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

async def hard_verify_ha():
    url = os.getenv("HASS_URL")
    token = os.getenv("HASS_TOKEN")
    entity_id = "light.kuche"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # SSL-Check (HA nutzt oft self-signed oder http lokal)
    verify_ssl = False

    async with httpx.AsyncClient(verify=verify_ssl) as client:
        print(f"--- HA HARD-VERIFY ({url}) ---")

        # 1. IST-Zustand prüfen
        try:
            resp = await client.get(f"{url}/api/states/{entity_id}", headers=headers)
            resp.raise_for_status()
            initial_state = resp.json().get("state")
            print(f"IST-Zustand von {entity_id}: {initial_state}")
        except Exception as e:
            print(f"FEHLER beim Abrufen des Zustands: {e}")
            return

        # 2. SCHALT-Befehl senden (Toggle)
        print(f"Sende TOGGLE-Befehl an {entity_id}...")
        try:
            resp = await client.post(
                f"{url}/api/services/light/toggle",
                headers=headers,
                json={"entity_id": entity_id}
            )
            resp.raise_for_status()
            print("HA hat den Befehl akzeptiert (HTTP 200/201).")
        except Exception as e:
            print(f"FEHLER beim Senden des Befehls: {e}")
            return

        # 3. Kurz warten (Hardware-Latenz)
        await asyncio.sleep(2)

        # 4. SOLL-Zustand prüfen
        try:
            resp = await client.get(f"{url}/api/states/{entity_id}", headers=headers)
            resp.raise_for_status()
            final_state = resp.json().get("state")
            print(f"NEUER Zustand von {entity_id}: {final_state}")

            if initial_state == final_state:
                print("!!! ALARM: ZUSTAND HAT SICH NICHT GEÄNDERT. HA IGNORIERT DEN BEFEHL !!!")
            else:
                print("ERFOLG: Zustand hat sich geändert. Die Hardware reagiert.")
        except Exception as e:
            print(f"FEHLER beim Abrufen des neuen Zustands: {e}")

if __name__ == "__main__":
    asyncio.run(hard_verify_ha())
