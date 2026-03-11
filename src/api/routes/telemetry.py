# ============================================================
# MTHO-GENESIS: Telemetry Aggregation Endpoint
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# ============================================================

"""
GET /api/mtho/telemetry – Aggregiert Echtzeit-Telemetrie
aus Watchdog (telemetry.json), Friction Guard, Event-Bus und API-Uptime.
"""

import json
import os
import time
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from starlette.responses import JSONResponse

router = APIRouter(prefix="/api/mtho", tags=["telemetry"])

TELEMETRY_PATH = os.path.join(
    os.getenv("MTHO_DATA_DIR", "c:/MTHO_CORE/data"),
    "telemetry.json",
)
_api_start_time = time.time()

API_TOKEN = os.getenv("MTHO_API_TOKEN", os.getenv("HA_WEBHOOK_TOKEN", ""))


def _verify_bearer(authorization: Optional[str] = Header(None)):
    if not API_TOKEN:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    if authorization[7:] != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


class WatchdogTelemetry(BaseModel):
    latency_ms: float = -1.0
    git_status: str = "UNKNOWN"
    mode: str = "UNKNOWN"
    timestamp: float = 0.0


class TelemetryResponse(BaseModel):
    watchdog: WatchdogTelemetry
    friction_violations: int = 0
    event_bus_connected: bool = False
    api_uptime_s: float = 0.0


@router.get("/telemetry")
async def get_telemetry():
    """Aggregierte System-Telemetrie (5s Cache empfohlen)."""

    watchdog = WatchdogTelemetry()
    try:
        if os.path.exists(TELEMETRY_PATH):
            with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            watchdog = WatchdogTelemetry(**raw)
    except Exception:
        pass

    friction_count = 0
    try:
        from src.api.middleware.friction_guard import FRICTION_STATE
        friction_count = FRICTION_STATE.get("violations", 0)
    except Exception:
        pass

    event_bus_ok = False
    try:
        from src.daemons.mtho_event_bus import MTHOEventBus
        event_bus_ok = True
    except Exception:
        pass

    result = TelemetryResponse(
        watchdog=watchdog,
        friction_violations=friction_count,
        event_bus_connected=event_bus_ok,
        api_uptime_s=round(time.time() - _api_start_time, 1),
    )

    response = JSONResponse(content=result.model_dump())
    response.headers["Cache-Control"] = "max-age=5"
    return response
