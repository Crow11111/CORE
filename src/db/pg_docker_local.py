# -*- coding: utf-8 -*-
"""
Lokaler PostgreSQL-Zugriff auf dem VPS: docker exec → psql (kein SSH-Hop).

Aktivierung: Environment ``OMEGA_INGEST_PG_LOCAL=1`` vor Import von
``ingest_queue_client`` (systemd ``Environment=``).
"""
from __future__ import annotations

import asyncio
import os
from typing import Tuple


def _docker_psql_cmd() -> list[str]:
    raw = (
        os.getenv("OMEGA_PG_DOCKER_EXEC")
        or "docker exec -i atlas_postgres_state psql -U atlas_admin -d atlas_state -q -t -A"
    ).strip()
    return raw.split()


async def run_pg_sql(sql: str, timeout: int = 30) -> Tuple[bool, str]:
    """Führt SQL via ``docker exec … psql`` auf dem Host aus."""
    cmd = _docker_psql_cmd()
    try:

        def _run():
            import subprocess

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            return subprocess.run(
                cmd,
                input=sql.encode("utf-8"),
                capture_output=True,
                timeout=timeout,
                env=env,
            )

        result = await asyncio.to_thread(_run)
    except Exception as e:
        return False, str(e)

    err = (result.stderr or b"").decode("utf-8", errors="replace")
    out = (result.stdout or b"").decode("utf-8", errors="replace")
    if result.returncode != 0 or "ERROR:" in err.upper() or "ERROR:" in out.upper():
        return False, err or out
    return True, out
