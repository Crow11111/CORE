# -*- coding: utf-8 -*-
"""VPS: Periodischer Dream-Worker (Ticket 12) — liest Pacemaker-JSON, ruft run_dream_cycle."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("vps_run_dream_worker")

_PACEMAKER_PATH = Path(
    os.environ.get("OMEGA_PACEMAKER_STATE_PATH", "/etc/omega/pacemaker.json")
)
_INTERVAL = float(os.environ.get("OMEGA_DREAM_INTERVAL_SEC", "60"))


def _load_pacemaker() -> dict:
    try:
        raw = _PACEMAKER_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        log.warning("pacemaker_read_failed path=%s err=%s", _PACEMAKER_PATH, e)
        return {}


async def _loop() -> None:
    from src.daemons import vps_dream_worker as dream

    while True:
        state = _load_pacemaker()
        v = state.get("V")
        r = state.get("R")
        pacemaker = {}
        if v is not None:
            pacemaker["V"] = v
        if r is not None:
            pacemaker["R"] = r

        try:
            out = await dream.run_dream_cycle(pacemaker)
            if out:
                log.info("dream_cycle_result %s", out)
        except Exception:
            log.exception("dream_cycle_failed")

        await asyncio.sleep(max(5.0, _INTERVAL))


def main() -> None:
    asyncio.run(_loop())


if __name__ == "__main__":
    sys.path.insert(0, os.environ.get("OMEGA_REPO_ROOT", "/opt/omega"))
    main()
