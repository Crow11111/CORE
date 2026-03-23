"""
Verifikations-Skript: Tool Calling
"""

import asyncio
import json
from src.connectors.home_assistant import HomeAssistantClient
from src.logic_core.tool_registry import ToolRegistry

async def dummy_tool(text: str, times: int = 1) -> str:
    """Dies ist ein Dummy-Tool zum Testen der Registry."""
    return f"Dummy-Tool wurde aufgerufen mit: '{text}' ({times} mal)"

async def main():
    print("--- [ CORE TOOL REGISTRY VERIFICATION ] ---")
    
    # 1. Dummy-Tool registrieren
    print("\n1. Registriere Dummy-Tool...")
    registry = ToolRegistry()
    registry.register(dummy_tool)
    
    schemas = registry.get_schemas()
    print("Generiertes Schema:")
    print(json.dumps(schemas, indent=2))
    
    # Tool aufrufen via Registry
    print("\n2. Rufe Dummy-Tool via Registry auf...")
    result = await registry.execute("dummy_tool", text="Hallo CORE", times=3)
    print(f"Ergebnis: {result}")
    
    # 3. Home Assistant Status abfragen
    print("\n3. Frage Status einer echten HA-Entität ab (zone.home)...")
    ha_client = HomeAssistantClient()
    try:
        # Wir testen ob HA da ist
        connected = await ha_client.check_connection()
        if not connected:
            print("[WARNUNG] Konnte nicht mit Home Assistant verbinden. Ist die URL in .env korrekt?")
        else:
            state = await ha_client.get_entity_state("zone.home")
            print(f"Status von 'zone.home': {state}")
            
            # Optional: Registriere die HA-Funktion als Tool
            print("\n4. Registriere HA-Methode als Tool und rufe sie ab...")
            registry.register(ha_client.get_entity_state, name="get_ha_state", description="Holt den Status einer HA Entität.")
            print(f"Schema für HA-Tool: {json.dumps(registry.get_schemas()[-1], indent=2)}")
            
            ha_result = await registry.execute("get_ha_state", entity_id="zone.home")
            print(f"Tool-Aufruf (get_ha_state) Ergebnis: {ha_result}")
    except Exception as e:
        print(f"[ERROR] Fehler beim HA-Zugriff: {e}")
    finally:
        await ha_client.close()
        
    print("\n[SUCCESS] Verifikation abgeschlossen.")

if __name__ == "__main__":
    asyncio.run(main())
