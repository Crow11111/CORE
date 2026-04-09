#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPS Kong: idempotent Service ``omega-core-backend`` + Route ``omega-core-status-route`` (Pfad ``/status``).

Upstream: Docker-Host (typ. docker0) — siehe ``infra/vps/kong/kong-deck-reference.yaml``.

Vorher: ``python -m src.scripts.vps_backup_snapshot``
"""
from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv

from src.config.vps_public_ports import (
    KONG_ADMIN_API_HOST_PORT,
    KONG_PROXY_HOST_PORT,
    OMEGA_BACKEND_HOST_PORT,
)

load_dotenv("/OMEGA_CORE/.env", override=True)

VPS_HOST = (os.getenv("VPS_HOST") or "").strip() or "187.77.68.250"
KONG_ADMIN_URL = (os.getenv("KONG_ADMIN_URL") or "").strip() or (
    f"http://{VPS_HOST}:{KONG_ADMIN_API_HOST_PORT}"
)

SERVICE_NAME = "omega-core-backend"
ROUTE_NAME = "omega-core-status-route"
CORE_SERVICE_URL = f"http://172.17.0.1:{OMEGA_BACKEND_HOST_PORT}"
STATUS_PATH = "/status"


def main() -> int:
    base = KONG_ADMIN_URL.rstrip("/")
    try:
        sr = httpx.get(f"{base}/services", timeout=15.0)
        sr.raise_for_status()
        sdata = sr.json().get("data") or []
        snames = {x.get("name") for x in sdata if isinstance(x, dict)}
    except Exception as exc:
        print("[FAIL] Kong /services nicht lesbar:", exc, file=sys.stderr)
        return 1

    try:
        rr = httpx.get(f"{base}/routes", timeout=15.0)
        rr.raise_for_status()
        rdata = rr.json().get("data") or []
    except Exception as exc:
        print("[FAIL] Kong /routes nicht lesbar:", exc, file=sys.stderr)
        return 1

    route_present = any(
        isinstance(rt, dict) and rt.get("name") == ROUTE_NAME for rt in rdata
    )

    if SERVICE_NAME in snames and route_present:
        print("[OK] bereits vorhanden")
        return 0

    if SERVICE_NAME not in snames:
        try:
            cr = httpx.post(
                f"{base}/services",
                json={"name": SERVICE_NAME, "url": CORE_SERVICE_URL},
                timeout=15.0,
            )
            if cr.status_code not in (200, 201):
                print(
                    "[FAIL] Service anlegen:",
                    cr.status_code,
                    cr.text[:400],
                    file=sys.stderr,
                )
                return 1
        except Exception as exc:
            print("[FAIL] Service POST:", exc, file=sys.stderr)
            return 1

    try:
        rtr = httpx.post(
            f"{base}/services/{SERVICE_NAME}/routes",
            json={
                "name": ROUTE_NAME,
                "paths": [STATUS_PATH],
                "strip_path": False,
                "protocols": ["http", "https"],
            },
            timeout=15.0,
        )
        if rtr.status_code not in (200, 201):
            print(
                "[FAIL] Route anlegen:",
                rtr.status_code,
                rtr.text[:400],
                file=sys.stderr,
            )
            return 1
    except Exception as exc:
        print("[FAIL] Route POST:", exc, file=sys.stderr)
        return 1

    print("[OK] Kong omega-core-backend + /status angelegt (Service + Route).")
    print(f"     Test: curl -sS http://{VPS_HOST}:{KONG_PROXY_HOST_PORT}{STATUS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
