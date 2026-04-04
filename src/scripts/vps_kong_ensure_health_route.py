#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPS Kong: idempotent Service + Route /health + request-termination (fester Text).

Vorher: python -m src.scripts.vps_backup_snapshot

Siehe docs/05_AUDIT_PLANNING/VPS_UMSETZUNGSPLAN_BACKUP_KONG_HEALTH.md
"""
from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv

from src.config.vps_public_ports import (
    KONG_ADMIN_API_HOST_PORT,
    KONG_PUBLIC_HEALTH_BODY,
    KONG_PUBLIC_HEALTH_PATH,
)

load_dotenv("/OMEGA_CORE/.env", override=True)

VPS_HOST = (os.getenv("VPS_HOST") or "").strip() or "187.77.68.250"
KONG_ADMIN_URL = (os.getenv("KONG_ADMIN_URL") or "").strip() or (
    f"http://{VPS_HOST}:{KONG_ADMIN_API_HOST_PORT}"
)

SERVICE_NAME = "omega-kong-health"
ROUTE_NAME = "omega-kong-health-route"


def main() -> int:
    base = KONG_ADMIN_URL.rstrip("/")
    try:
        sr = httpx.get(f"{base}/services", timeout=15.0)
        sr.raise_for_status()
        names = {x.get("name") for x in (sr.json().get("data") or []) if isinstance(x, dict)}
        if SERVICE_NAME in names:
            print(f"[OK] Kong-Service '{SERVICE_NAME}' existiert bereits — keine Änderung.")
            return 0
    except Exception as exc:
        print("[FAIL] Kong /services nicht lesbar:", exc, file=sys.stderr)
        return 1

    # Dummy-Upstream; request-termination beantwortet ohne Proxy (siehe Kong-Plugin).
    try:
        cr = httpx.post(
            f"{base}/services",
            json={"name": SERVICE_NAME, "url": "https://example.com:443"},
            timeout=15.0,
        )
        if cr.status_code not in (200, 201):
            print("[FAIL] Service anlegen:", cr.status_code, cr.text[:400], file=sys.stderr)
            return 1
    except Exception as exc:
        print("[FAIL] Service POST:", exc, file=sys.stderr)
        return 1

    path = KONG_PUBLIC_HEALTH_PATH if KONG_PUBLIC_HEALTH_PATH.startswith("/") else f"/{KONG_PUBLIC_HEALTH_PATH}"
    try:
        rr = httpx.post(
            f"{base}/services/{SERVICE_NAME}/routes",
            json={
                "name": ROUTE_NAME,
                "paths": [path],
                "strip_path": False,
                "protocols": ["http", "https"],
            },
            timeout=15.0,
        )
        if rr.status_code not in (200, 201):
            print("[FAIL] Route anlegen:", rr.status_code, rr.text[:400], file=sys.stderr)
            return 1
    except Exception as exc:
        print("[FAIL] Route POST:", exc, file=sys.stderr)
        return 1

    try:
        pr = httpx.post(
            f"{base}/services/{SERVICE_NAME}/plugins",
            json={
                "name": "request-termination",
                "config": {
                    "status_code": 200,
                    "body": KONG_PUBLIC_HEALTH_BODY,
                    "content_type": "text/plain; charset=utf-8",
                },
            },
            timeout=15.0,
        )
        if pr.status_code not in (200, 201):
            print("[FAIL] Plugin anlegen:", pr.status_code, pr.text[:400], file=sys.stderr)
            return 1
    except Exception as exc:
        print("[FAIL] Plugin POST:", exc, file=sys.stderr)
        return 1

    print("[OK] Kong /health angelegt (Service + Route + request-termination).")
    print("     Test: curl -sS http://", VPS_HOST, ":32776", path, sep="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
