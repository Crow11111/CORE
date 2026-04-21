# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
OpenClaw Gateway Client (Hostinger).
Liest VPS_HOST und OPENCLAW_GATEWAY_TOKEN aus .env.
- CORE → OC: send_message_to_agent() (POST /v1/responses)
- OC → CORE: GQA F2 Webhook-Push (POST /api/oc/webhook) oder Fallback fetch_oc_submissions (SFTP).
"""
import os
import asyncio
import httpx
import json
import logging
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.time_metric import get_friction_timeout

# LOGGING SETUP
logger = logging.getLogger("OPENCLAW_CLIENT")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()

VPS_HOST = os.getenv("VPS_HOST", "")
OPENCLAW_GATEWAY_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
OPENCLAW_GATEWAY_PORT = int(os.getenv("OPENCLAW_GATEWAY_PORT", "18789"))
BACKEND_INTERNAL_URL = os.getenv("BACKEND_INTERNAL_URL", f"http://{VPS_HOST}:8000")

# Pfad auf dem VPS, in dem OC Einreichungen für den Rat ablegt (OC → CORE)
OC_RAT_SUBMISSIONS_DIR = "/var/lib/openclaw/workspace/rat_submissions"


class CausalReceipt(BaseModel):
    """Kausale Quittung für den Systembus."""
    base_hash_t: str
    compute_latency_ms: int


class DimensionalShift(BaseModel):
    """Topologische Verschiebung im kognitiven Raum."""
    x_car_cdr_delta: float = 0.0
    y_gravitation_delta: float = 0.0
    z_resistance_delta: float = 0.0


class JSONDelta(BaseModel):
    """Das I-Vektor Schema (Kognitiver Tensor)."""
    causal_receipt: CausalReceipt
    dimensional_shift: DimensionalShift
    semantic_nodes_hot: Dict[str, float] = Field(default_factory=dict)
    exhaust: Dict[str, str] = Field(default_factory=dict)


class OpenClawClient:
    """
    Klasse zur Interaktion mit dem OpenClaw Gateway und dem CORE Systembus.
    Implementiert das I-Vektor Protokoll (Causal Hashing).
    """

    def __init__(
        self,
        vps_host: str = VPS_HOST,
        token: str = OPENCLAW_GATEWAY_TOKEN,
        port: int = OPENCLAW_GATEWAY_PORT,
        backend_url: str = BACKEND_INTERNAL_URL
    ):
        self.vps_host = vps_host
        self.token = token
        self.port = port
        self.backend_url = backend_url
        self.current_state_hash: Optional[str] = None

    def get_gateway_url(self, path: str = "") -> str:
        """Basis-URL des OpenClaw-Gateways."""
        base = f"http://{self.vps_host}:{self.port}"
        if not path:
            return base
        return f"{base}{path}" if path.startswith("/") else f"{base}/{path}"

    def get_auth_headers(self) -> dict:
        """Header mit Gateway-Token."""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def is_configured(self) -> bool:
        """Prüft Konfiguration."""
        return bool(self.vps_host and self.token)

    async def check_gateway_async(self, timeout: float = 5.0) -> tuple[bool, str]:
        """Testet die Erreichbarkeit des OpenClaw-Gateways."""
        if not self.is_configured():
            return False, "Nicht konfiguriert (VPS_HOST oder OPENCLAW_GATEWAY_TOKEN fehlt)"
        try:
            url = self.get_gateway_url("/")
            timeout_friction = get_friction_timeout(timeout)
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_friction)) as client:
                r = await client.get(url, headers=self.get_auth_headers())
                r.raise_for_status()
                return True, f"OK {r.status_code} – Gateway erreichbar"
        except Exception as e:
            return False, f"Verbindungsfehler: {e}"

    async def push_to_bus(self, delta_dict: dict) -> str:
        """
        Sendet das JSON-Delta an den CORE Systembus (/api/v1/bus/delta).
        Aktualisiert den lokalen state_hash.
        """
        try:
            # Validierung durch Pydantic
            delta = JSONDelta(**delta_dict)
            url = f"{self.backend_url}/api/v1/bus/delta"
            
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=delta.model_dump())
                r.raise_for_status()
                result = r.json()
                new_hash = result.get("new_state_hash", "UNKNOWN")
                self.current_state_hash = new_hash
                
                # Axiom A7: Logging Loop für die Kausalitätskette
                logger.info(f"BUS_INTEGRATION_SUCCESS | state_hash_t1: {new_hash}")
                return new_hash
        except Exception as e:
            logger.error(f"BUS_INTEGRATION_FAILED | error: {e}")
            return "ERROR"

    async def send_message_to_agent_async(
        self,
        text: str,
        agent_id: str = "main",
        user: str | None = None,
        timeout: float = 30.0,
    ) -> tuple[bool, str]:
        """
        Sendet Nachricht an OC Agent und injiziert Tensor automatisch in den Bus.
        """
        if not self.is_configured():
            return False, "Nicht konfiguriert"
        
        try:
            url = self.get_gateway_url("/v1/responses")
            headers = {
                **self.get_auth_headers(),
                "Content-Type": "application/json",
                "x-openclaw-agent-id": agent_id,
            }
            body: dict = {"model": "openclaw", "input": text}
            if user:
                body["user"] = user
            
            timeout_friction = get_friction_timeout(timeout)
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_friction)) as client:
                r = await client.post(url, headers=headers, json=body)
                r.raise_for_status()
                data = r.json()
                
                out = data.get("output") or []
                parts = []
                for item in out if isinstance(out, list) else []:
                    if isinstance(item, dict):
                        text_part = item.get("text", "")
                        if text_part:
                            parts.append(text_part)
                            # Automatische Erkennung eines Tensors (JSON-Delta)
                            try:
                                if "causal_receipt" in text_part and "dimensional_shift" in text_part:
                                    # Wir versuchen das JSON zu extrahieren, falls es eingebettet ist
                                    start = text_part.find("{")
                                    end = text_part.rfind("}") + 1
                                    if start != -1 and end != 0:
                                        potential_json = text_part[start:end]
                                        delta_data = json.loads(potential_json)
                                        await self.push_to_bus(delta_data)
                            except (json.JSONDecodeError, ValueError):
                                pass

                response_text = "".join(parts).strip() if parts else str(data)[:500]
                return True, response_text or "(leere Antwort)"
        except Exception as e:
            return False, f"Fehler: {e}"


# --- BACKWARD COMPATIBILITY WRAPPERS ---

_client_instance = OpenClawClient()

def gateway_url(path: str = "") -> str:
    return _client_instance.get_gateway_url(path)

def auth_headers() -> dict:
    return _client_instance.get_auth_headers()

def is_configured() -> bool:
    return _client_instance.is_configured()

async def check_gateway_async(timeout: float = 5.0) -> tuple[bool, str]:
    return await _client_instance.check_gateway_async(timeout)

def check_gateway(timeout: float = 5.0) -> tuple[bool, str]:
    return asyncio.run(check_gateway_async(timeout))

async def send_message_to_agent_async(
    text: str,
    agent_id: str = "main",
    user: str | None = None,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    return await _client_instance.send_message_to_agent_async(text, agent_id, user, timeout)

def send_message_to_agent(
    text: str,
    agent_id: str = "main",
    user: str | None = None,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    return asyncio.run(send_message_to_agent_async(text, agent_id, user, timeout))

async def send_event_to_oc_brain_async(
    event_type: str,
    data: dict,
    timeout: float = 15.0,
) -> tuple[bool, str]:
    formatted_msg = f"[CORE_EVENT] type={event_type}\n{json.dumps(data, ensure_ascii=False, indent=2)}"
    return await send_message_to_agent_async(
        text=formatted_msg,
        agent_id="main",
        user="core_event_bus",
        timeout=timeout,
    )

def send_event_to_oc_brain(
    event_type: str,
    data: dict,
    timeout: float = 15.0,
) -> tuple[bool, str]:
    return asyncio.run(send_event_to_oc_brain_async(event_type, data, timeout))
