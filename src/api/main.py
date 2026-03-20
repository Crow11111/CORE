# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from loguru import logger

# Temporär auskommentiert wegen ImportError
# from src.api.routes import id_safe

from src.api.routes import whatsapp_webhook, ha_webhook, oc_channel, core_knowledge, core_voice, core_events, github_webhook, omega_matrix, omega_thought, telemetry, chat, dictate, voice_bridge, jarvis_mri_coupler

from src.api.middleware.veto_gate import VetoGateMiddleware
from src.api.middleware.friction_guard import FrictionGuardMiddleware

_event_bus = None
_agent_pool = None

from collections import deque
import time as _time

_log_buffer: deque[dict] = deque(maxlen=200)


def _log_sink(message):
    record = message.record
    _log_buffer.append({
        "ts": record["time"].strftime("%H:%M:%S"),
        "level": record["level"].name,
        "msg": record["message"],
        "src": f"{record['name']}:{record['function']}",
    })


logger.add(_log_sink, format="{message}", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """CORE API Lifecycle: Ephemeral Pool + Event-Bus Startup/Shutdown."""
    global _event_bus, _agent_pool

    try:
        from src.agents.scout_core_handlers import scout_fusion_init
        _agent_pool = await scout_fusion_init()
        logger.info("[API] CORE Agent Pool initialisiert")
    except Exception as exc:
        logger.error("[API] Agent Pool Init fehlgeschlagen: {} – API laeuft weiter", exc)

    hass_url = (os.getenv("HASS_URL") or "").strip()
    hass_token = (os.getenv("HASS_TOKEN") or "").strip()
    if hass_url and hass_token:
        try:
            from src.daemons.core_event_bus import start_event_bus
            _event_bus = await start_event_bus()
            logger.info("[API] Event-Bus gestartet (HASS_URL konfiguriert)")
        except Exception as exc:
            logger.error("[API] Event-Bus Start fehlgeschlagen: {} – API laeuft weiter", exc)
    else:
        logger.info("[API] Event-Bus uebersprungen (HASS_URL/HASS_TOKEN nicht gesetzt)")

    # --- SYNC RELAY ---
    webhook_secret = (os.getenv("CORE_WEBHOOK_SECRET") or "").strip()
    if webhook_secret:
        try:
            import threading
            import asyncio as _aio
            from aiohttp import web as _aio_web

            def _run_sync_relay():
                from src.network.core_sync_relay import app as sync_relay_app
                loop = _aio.new_event_loop()
                _aio.set_event_loop(loop)
                try:
                    loop.run_until_complete(_aio_web.run_app(sync_relay_app, port=8049, handle_signals=False, print=lambda *a: None))
                except OSError as e:
                    if e.errno == 10048:
                        logger.warning("[API] Sync Relay Port 8049 bereits belegt (vermutlich alter Reload-Prozess) -- uebersprungen")
                    else:
                        raise

            _sync_relay_thread = threading.Thread(target=_run_sync_relay, daemon=True, name="core-sync-relay")
            _sync_relay_thread.start()
            logger.info("[API] Sync Relay gestartet (Port 8049)")
        except Exception as exc:
            logger.error("[API] Sync Relay Start fehlgeschlagen: {} – API laeuft weiter", exc)
    else:
        logger.info("[API] Sync Relay uebersprungen (CORE_WEBHOOK_SECRET nicht gesetzt)")

    yield

    if _event_bus is not None:
        try:
            await _event_bus.stop()
            logger.info("[API] Event-Bus gestoppt")
        except Exception as exc:
            logger.warning("[API] Event-Bus Stop Fehler: {}", exc)

    if _agent_pool is not None:
        try:
            await _agent_pool.stop()
            logger.info("[API] Agent Pool GC gestoppt")
        except Exception as exc:
            logger.warning("[API] Agent Pool Stop Fehler: {}", exc)


app = FastAPI(
    title="CORE API",
    description="Main Backend Interface for CORE Operations",
    version="1.0.0",
    lifespan=lifespan,
)

# Veto Gate: Veto-Middleware für kritische Operationen (DELETE, Config, Token, Backup)
app.add_middleware(VetoGateMiddleware)
# Friction Guard: Scannt LLM-Output auf Simulation (Heresy-Trap)
app.add_middleware(FrictionGuardMiddleware)

ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrierung der Routen (Webhooks + OpenClaw Channel)
app.include_router(whatsapp_webhook.router)
app.include_router(ha_webhook.router)
app.include_router(oc_channel.router)
app.include_router(core_knowledge.router)
app.include_router(core_voice.router)
app.include_router(core_events.router)
app.include_router(github_webhook.router)
app.include_router(omega_matrix.router)
app.include_router(omega_thought.router)
app.include_router(telemetry.router)
app.include_router(chat.router)
app.include_router(jarvis_mri_coupler.router)
app.include_router(voice_bridge.router)
app.include_router(dictate.router)
app.include_router(voice_bridge.router)
# app.include_router(id_safe.router)

@app.get("/")
def read_root():
    return {"status": "online", "system": "CORE", "version": "1.0.0"}


def _cockpit_category(entry: dict) -> str:
    """
    Kategorien fuer Cockpit-Ticker (Frontend blendet per Toggle ein/aus).
    """
    msg = entry.get("msg") or ""
    if not str(msg).strip():
        return "skip"
    level = (entry.get("level") or "INFO").upper()
    mlow = msg.lower()
    if any(
        k in mlow
        for k in (
            "kernel:",
            "[kernel",
            "systemd",
            " oom ",
            "oom-killer",
            "segfault",
            "dbus",
        )
    ):
        return "host"
    if "[EVENT-BUS]" in msg:
        if "[CRITICAL]" in msg:
            return "ha_crit"
        if "[WARNING]" in msg:
            return "ha_warn"
        if "[INFO]" in msg:
            return "ha_sensor"
        return "ha_sensor"
    if level == "ERROR":
        return "system"
    if level == "WARNING":
        return "heuristic"
    return "core"


@app.get("/api/logs")
def get_logs(since: int = 0, limit: int = 50):
    """Liefert die letzten Log-Eintraege aus dem Ringbuffer."""
    logs = list(_log_buffer)
    if since > 0:
        logs = logs[since:]
    return {"logs": logs[-limit:], "total": len(_log_buffer)}


@app.get("/api/cockpit_feed")
def get_cockpit_feed(limit: int = 250):
    """Alle Logzeilen mit cockpit_category — Frontend filtert (Kein Server-Vorhalten)."""
    n = max(1, min(int(limit), 400))
    raw = list(_log_buffer)[-n:]
    out = []
    for e in raw:
        cat = _cockpit_category(e)
        if cat == "skip":
            continue
        row = dict(e)
        row["category"] = cat
        out.append(row)
    return {"logs": out, "total_ring": len(_log_buffer)}


@app.get("/api/cockpit_ticker")
def get_cockpit_ticker(limit: int = 100):
    """Legacy: ohne HA-Sensor-INFO (nutzt Cockpit lieber /api/cockpit_feed + Toggles)."""
    logs = [e for e in _log_buffer if _cockpit_category(e) != "ha_sensor"]
    logs = [e for e in logs if _cockpit_category(e) != "skip"]
    out = logs[-max(1, min(limit, 200)) :]
    return {"logs": out, "total": len(logs), "filtered_from": len(_log_buffer)}


@app.get("/health", response_class=HTMLResponse)
def health_dashboard():
    """CORE Command Post: Health + Diktat + Chat -- fuer Cursor Simple Browser."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "health.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/v1/chat/completions/health")
def jarvis_wrong_base_health_compat() -> dict:
    """Kompatibilitaet: KDE-Jarvis-Plasmoid haengt '/health' an die konfigurierte Basis-URL.

    Wenn die Basis fälschlich ``.../v1/chat/completions`` ist, wird sonst
    ``.../v1/chat/completions/health`` (404) aufgerufen. Diese Route liefert 200.
    Korrekte Konfiguration bleibt: nur Origin, z. B. ``http://127.0.0.1:8000``.
    """
    return {"status": "ok", "note": "jarvis-compat-wrong-llm-base"}


@app.get("/voice-bridge", response_class=HTMLResponse)
def voice_bridge_page():
    """Stimme rein/raus ueber CORE-API (unabhaengig von AI Studio Voice)."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "voice_bridge.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/status")
def system_status() -> dict:
    """Systemstatus inkl. Event-Bus Metriken."""
    hass_configured = bool(
        (os.getenv("HASS_URL") or "").strip()
        and (os.getenv("HASS_TOKEN") or "").strip()
    )
    bus_stats = _event_bus.stats if _event_bus is not None else None
    return {
        "system": "CORE",
        "version": "1.0.0",
        "event_bus": {
            "hass_configured": hass_configured,
            "running": _event_bus is not None,
            "stats": bus_stats,
        },
        "agent_pool": {
            "active": _agent_pool is not None,
        },
        "sync_relay": {
            "enabled": bool((os.getenv("CORE_WEBHOOK_SECRET") or "").strip()),
            "port": 8049,
        },
    }

if __name__ == "__main__":
    import uvicorn
    # Test-Aufruf lokal (z.B. python -m src.api.main)
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
