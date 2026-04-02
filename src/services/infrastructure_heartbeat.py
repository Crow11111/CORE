import asyncio
import os
import subprocess
import time
import json
import httpx
from datetime import datetime, timezone
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from src.db.multi_view_client import _run_pg_sql
from src.network import openclaw_client

# TICKET_10 / Tests: gebundenes Symbol für patch.object(ih, "check_gateway_async", ...)
check_gateway_async = openclaw_client.check_gateway_async

# CORE Infrastructure Heartbeat Service
# Vector: 2210 | Resonance: 0221 | Delta: 0.049

load_dotenv()

CHECK_INTERVAL = 60  # Sekunden

# TICKET_10: Autonomie-Veto + Pathologie-Log (NMI/Asystole)
AUTONOMY_VETO_FLAG_PATH = Path("/tmp/omega_autonomy_veto.flag")
DEFAULT_PACEMAKER_PATHOLOGY_LOG = Path("/tmp/omega_pacemaker_pathology.log")


def _pacemaker_pathology_log_path() -> Path:
    env_p = os.environ.get("OMEGA_PACEMAKER_PATHOLOGY_LOG")
    if env_p:
        return Path(env_p)
    return DEFAULT_PACEMAKER_PATHOLOGY_LOG


async def apply_openclaw_autonomy_veto_if_needed() -> None:
    """
    Prüft das OpenClaw-Gateway (check_gateway_async); bei Fehlschlag: Veto-Flag + Pathologie-Log (asystole).
    """
    ok, msg = await check_gateway_async()
    if ok:
        return

    AUTONOMY_VETO_FLAG_PATH.write_text("Gateway Down", encoding="utf-8")
    log_path = _pacemaker_pathology_log_path()
    line = (
        f"{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')} "
        "PATHOLOGY asystole / openclaw gateway dead — autonomy veto "
        f"(check_gateway: {msg})\n"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)
    logger.error(
        "[PACEMAKER] asystole / openclaw gateway dead — wrote autonomy veto flag %s",
        AUTONOMY_VETO_FLAG_PATH,
    )

class InfrastructureSentinel:
    def __init__(self):
        self.vps_host = os.getenv("VPS_HOST", "187.77.68.250")
        self.scout_ip = os.getenv("SCOUT_IP", "192.168.178.54")
        self.hass_url = os.getenv("HASS_URL", f"https://{self.scout_ip}:8123")
        self.go2rtc_url = os.getenv("GO2RTC_BASE_URL", f"http://{self.scout_ip}:1984")
        
        # VPS Tokens
        self.evolution_key = os.getenv("EVOLUTION_API_KEY", "")
        self.monica_token = os.getenv("MONICA_TOKEN", "")

    async def check_dreadnought_service(self, service_name: str) -> bool:
        """Prüft systemd Status auf dem lokalen Dreadnought-System."""
        try:
            # Wir mappen service_name auf die tatsächlichen systemd Units
            # In CLAUDE.md heißen sie omega-backend, omega-frontend, etc.
            cmd = ["systemctl", "is-active", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip() == "active"
        except Exception as e:
            logger.error(f"Fehler bei systemctl Check ({service_name}): {e}")
            return False

    async def check_http(self, url: str, headers: dict = None, timeout: float = 5.0) -> bool:
        """Prüft HTTP Erreichbarkeit."""
        try:
            async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
                resp = await client.get(url, headers=headers)
                return resp.status_code < 400
        except Exception:
            return False

    async def update_status(self, node: str, service: str, status: str, metadata: dict = None):
        """Aktualisiert den Status in der VPS-Datenbank."""
        meta_s = json.dumps(metadata or {}, ensure_ascii=False)
        sql = f"""
        UPDATE core_infrastructure
        SET status = '{status}',
            last_seen = CURRENT_TIMESTAMP,
            metadata = metadata || '{meta_s}'::jsonb
        WHERE node_name = '{node}' AND service_name = '{service}';
        """
        ok, err = await _run_pg_sql(sql)
        if not ok:
            logger.error(f"Status-Update fehlgeschlagen ({node}/{service}): {err}")

    async def run_once(self):
        logger.info("[SENTINEL] Starte Heartbeat-Check...")
        
        # 1. Dreadnought Checks
        dreadnought_services = [
            "omega-backend", "omega-frontend", "omega-event-bus", 
            "omega-watchdog", "omega-vision", "omega-audio"
        ]
        for svc in dreadnought_services:
            is_active = await self.check_dreadnought_service(svc)
            await self.update_status("Dreadnought", svc, "active" if is_active else "inactive")

        # 2. Scout Checks
        # Home Assistant
        hass_ok = await self.check_http(f"{self.hass_url}/api/", headers={"Authorization": f"Bearer {os.getenv('HASS_TOKEN')}"})
        await self.update_status("Scout", "homeassistant", "active" if hass_ok else "inactive")
        
        # go2rtc
        go2rtc_ok = await self.check_http(self.go2rtc_url)
        await self.update_status("Scout", "go2rtc", "active" if go2rtc_ok else "inactive")

        # 3. VPS Checks
        vps_checks = [
            ("chroma-uvmy", f"http://{self.vps_host}:32768/api/v2/heartbeat", None),
            ("openclaw-admin", f"http://{self.vps_host}:18789/api/status", None),
            ("evolution-api", f"http://{self.vps_host}:55775/instance/fetchInstances", {"apikey": self.evolution_key} if self.evolution_key else None),
            ("kong", f"http://{self.vps_host}:32773/status", None),
            ("monica", f"http://{self.vps_host}:32769/api/contacts", {"Authorization": f"Bearer {self.monica_token}"} if self.monica_token else None),
            ("atlas_agi_core", f"http://{self.vps_host}:8080/status", None),
        ]
        
        for svc, url, headers in vps_checks:
            ok = await self.check_http(url, headers=headers)
            await self.update_status("VPS", svc, "active" if ok else "inactive")

        await apply_openclaw_autonomy_veto_if_needed()

        logger.info("[SENTINEL] Heartbeat-Check abgeschlossen.")

    async def run_forever(self):
        logger.info(f"[SENTINEL] Heartbeat Service gestartet (Intervall: {CHECK_INTERVAL}s)")
        while True:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Fehler im Heartbeat-Loop: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    import sys
    sentinel = InfrastructureSentinel()
    if "--once" in sys.argv:
        asyncio.run(sentinel.run_once())
    else:
        asyncio.run(sentinel.run_forever())
