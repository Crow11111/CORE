import subprocess
from loguru import logger
from src.logic_core.tool_registry import ToolRegistry

registry = ToolRegistry()

# ----------------- LOCAL DESKTOP TOOLS -----------------

def get_wpctl_base_cmd():
    return ["sudo", "-u", "mth", "env", "XDG_RUNTIME_DIR=/run/user/1000", "wpctl"]

def get_app_base_cmd():
    return ["sudo", "-u", "mth", "env", "XDG_RUNTIME_DIR=/run/user/1000", "DISPLAY=:0"]

def set_volume(level: int) -> str:
    """Setzt die Systemlautstärke (0-100)."""
    try:
        level = max(0, min(100, level))
        cmd = get_wpctl_base_cmd() + ["set-volume", "@DEFAULT_AUDIO_SINK@", f"{level}%"]
        subprocess.run(cmd, check=True)
        return f"Lautstärke auf {level}% gesetzt."
    except Exception as e:
        logger.error(f"Fehler bei set_volume: {e}")
        return f"Fehler: {e}"

def mute_toggle() -> str:
    """Schaltet die Systemlautstärke stumm oder hebt die Stummschaltung auf."""
    try:
        cmd = get_wpctl_base_cmd() + ["set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]
        subprocess.run(cmd, check=True)
        return "Mute getoggelt."
    except Exception as e:
        logger.error(f"Fehler bei mute_toggle: {e}")
        return f"Fehler: {e}"

def start_app(app_name: str) -> str:
    """Startet eine Desktop-Anwendung (z.B. 'firefox', 'konsole')."""
    try:
        cmd = get_app_base_cmd() + [app_name]
        subprocess.Popen(cmd, start_new_session=True)
        return f"App '{app_name}' gestartet."
    except Exception as e:
        logger.error(f"Fehler bei start_app: {e}")
        return f"Fehler beim Starten von {app_name}: {e}"

# ----------------- HOME ASSISTANT TOOLS -----------------
import asyncio
from src.connectors.home_assistant import HomeAssistantClient

async def call_ha_service(domain: str, service: str, entity_id: str) -> str:
    """Ruft einen Service in Home Assistant auf (z.B. domain='light', service='turn_on', entity_id='light.buero')."""
    client = HomeAssistantClient()
    try:
        success = await client.call_ha_service(domain, service, entity_id)
        return f"Service {domain}.{service} für {entity_id} {'erfolgreich' if success else 'fehlgeschlagen'}."
    except Exception as e:
        return f"Fehler: {e}"
    finally:
        await client.close()

async def get_ha_state(entity_id: str) -> str:
    """Holt den aktuellen Status einer Home Assistant Entity (z.B. 'light.buero')."""
    client = HomeAssistantClient()
    try:
        state = await client.get_entity_state(entity_id)
        return f"Status von {entity_id}: {state}"
    except Exception as e:
        return f"Fehler: {e}"
    finally:
        await client.close()


registry.register(set_volume)
registry.register(mute_toggle)
registry.register(start_app)
registry.register(call_ha_service)
registry.register(get_ha_state)

