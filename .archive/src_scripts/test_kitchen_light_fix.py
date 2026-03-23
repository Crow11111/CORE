import asyncio
import os
from dotenv import load_dotenv
from src.connectors.home_assistant import HomeAssistantClient

load_dotenv("/OMEGA_CORE/.env")

async def test_kitchen_light():
    client = HomeAssistantClient()
    try:
        # Test 1: Status abrufen
        state = await client.get_entity_state("light.kuche")
        print(f"Status light.kuche (Küche): {state}")

        # Test 2: Toggle
        print("Toggling light.kuche...")
        success = await client.call_ha_service("light", "toggle", "light.kuche")
        print(f"Toggle erfolgreich: {success}")

        # Test 3: Status abrufen nach Toggle
        new_state = await client.get_entity_state("light.kuche")
        print(f"Neuer Status: {new_state}")

    except Exception as e:
        print(f"Fehler beim Test: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_kitchen_light())
