#!/usr/bin/env python3
"""
VPS-Stack-Verifikation: Container, Chroma v2 Heartbeat, Kong laut `kong-deck-reference.yaml`
(evolution-api + /evo + omega-kong-health + `/health` + omega-core-backend + `/status`;
Proxy-GET `/health` mit Body `OMEGA_KONG_HEALTH_OK`; optional Hinweis zu `/status`).
Siehe docs/BIBLIOTHEK_KERN_DOKUMENTE.md, VPS_FULL_STACK_SETUP, VPS_KNOTEN_UND_FLUSSE, KONSOLIDIERTER_VERKEHRSPLAN §8.
"""
import os
import subprocess
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

from src.config.vps_public_ports import (
    CHROMA_UVMY_HOST_PORT,
    EVOLUTION_API_HOST_PORT,
    KONG_ADMIN_API_HOST_PORT,
    KONG_PROXY_HOST_PORT,
    KONG_PUBLIC_HEALTH_BODY,
    KONG_PUBLIC_HEALTH_PATH,
    MONICA_HTTP_HOST_PORT,
)

from src.scripts.verify_vps_docker_port_contract import verify_docker_ps_lines_tabbed

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=True)

VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250")
VPS_SSH_KEY = os.getenv("VPS_SSH_KEY", "/home/mth/.ssh/id_ed25519_hostinger")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", str(CHROMA_UVMY_HOST_PORT)))
EVOLUTION_API_URL = (os.getenv("EVOLUTION_API_URL") or "").strip() or (
    f"http://{VPS_HOST}:{EVOLUTION_API_HOST_PORT}"
)
MONICA_URL = (os.getenv("MONICA_URL") or "").strip() or (
    f"http://{VPS_HOST}:{MONICA_HTTP_HOST_PORT}"
)
KONG_ADMIN_URL = (os.getenv("KONG_ADMIN_URL") or "").strip() or (
    f"http://{VPS_HOST}:{KONG_ADMIN_API_HOST_PORT}"
)

def run_ssh(cmd: str) -> tuple[int, str]:
    full = f'ssh -o ConnectTimeout=15 -o BatchMode=yes -i "{VPS_SSH_KEY}" root@{VPS_HOST} "{cmd}"'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=45)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def _container_up(lines: list[str], substring: str) -> bool:
    return any(substring in l and "Up" in l for l in lines)


def _kong_service_id_to_name(sdata: list) -> dict[str, str]:
    out: dict[str, str] = {}
    for x in sdata:
        if not isinstance(x, dict):
            continue
        sid = x.get("id")
        name = x.get("name")
        if sid and name:
            out[str(sid)] = str(name)
    return out


def _kong_route_service_name(rt: dict, id_to_name: dict[str, str]) -> str | None:
    svc = rt.get("service")
    if svc is None:
        return None
    if isinstance(svc, dict):
        n = svc.get("name")
        if n:
            return str(n)
        sid = svc.get("id")
        if sid is not None:
            return id_to_name.get(str(sid))
    return None


def _verify_kong_matches_deck_reference(lines: list[str]) -> tuple[bool, str]:
    """
    KONSOLIDIERTER_VERKEHRSPLAN §8.3: Repo-Deck-Referenz vs. Admin-API (keine neuen Routen hier).
    """
    if not _container_up(lines, "kong-s7rk-kong"):
        return True, "[--] Kong-Container nicht Up — Deck-Check übersprungen"
    base = KONG_ADMIN_URL.rstrip("/")
    try:
        sr = httpx.get(f"{base}/services", timeout=10.0)
        rr = httpx.get(f"{base}/routes", timeout=10.0)
        if sr.status_code != 200:
            return False, f"Kong /services HTTP {sr.status_code}"
        if rr.status_code != 200:
            return False, f"Kong /routes HTTP {rr.status_code}"
        sdata = sr.json().get("data") or []
        rdata = rr.json().get("data") or []
        snames = {x.get("name") for x in sdata if isinstance(x, dict)}
        id_to_name = _kong_service_id_to_name(sdata)
        paths: list[str] = []
        for rt in rdata:
            if isinstance(rt, dict):
                paths.extend(rt.get("paths") or [])
        if "evolution-api" not in snames:
            return False, "Kong: Service evolution-api fehlt (Deck-Referenz)"
        if "/evo" not in paths:
            return False, "Kong: Route-Pfad /evo fehlt (Deck-Referenz)"
        hp = KONG_PUBLIC_HEALTH_PATH.strip()
        if not hp.startswith("/"):
            hp = "/" + hp
        if "omega-kong-health" not in snames:
            return False, "Kong: Service omega-kong-health fehlt (Proxy /health)"
        if hp not in paths:
            return False, f"Kong: Route-Pfad {hp} fehlt (Health)"
        if "omega-core-backend" not in snames:
            return False, "Kong: Service omega-core-backend fehlt (Deck-Referenz)"
        if "/status" not in paths:
            return False, "Kong: Route-Pfad /status fehlt (omega-core-backend)"
        status_ok = False
        for rt in rdata:
            if not isinstance(rt, dict):
                continue
            rpaths = rt.get("paths") or []
            if "/status" not in rpaths:
                continue
            if _kong_route_service_name(rt, id_to_name) == "omega-core-backend":
                status_ok = True
                break
        if not status_ok:
            return (
                False,
                "Kong: keine Route mit Pfad /status für Service omega-core-backend (service.id/name)",
            )
        return True, (
            "[OK] Kong Deck-Referenz (evolution, /evo, health, omega-core-backend, /status)"
        )
    except Exception as exc:
        return False, f"Kong Deck-Check: {exc}"


def _verify_kong_proxy_health(lines: list[str]) -> tuple[bool, str]:
    """HTTP GET über öffentlichen Proxy-Port — Body muss KONG_PUBLIC_HEALTH_BODY enthalten."""
    if not _container_up(lines, "kong-s7rk-kong"):
        return True, "[--] Kong Proxy /health übersprungen (kein Kong)"
    hp = KONG_PUBLIC_HEALTH_PATH.strip()
    if not hp.startswith("/"):
        hp = "/" + hp
    url = f"http://{VPS_HOST}:{KONG_PROXY_HOST_PORT}{hp}"
    try:
        r = httpx.get(url, timeout=10.0)
        if r.status_code == 200 and KONG_PUBLIC_HEALTH_BODY in r.text:
            return True, "[OK] Kong Proxy /health (HTTP + Body)"
        return False, f"[FAIL] Kong Proxy /health HTTP {r.status_code} body={r.text[:120]!r}"
    except Exception as exc:
        return False, f"[FAIL] Kong Proxy /health {exc}"


def main():
    ok = True
    # 1) Docker ps – Pflicht-Container
    code, out = run_ssh(
        "docker ps --format '{{.Names}}\\t{{.Status}}\\t{{.Ports}}'"
    )
    if code != 0:
        print("[FAIL] VPS SSH oder docker ps:", out[:400])
        ok = False
    else:
        lines = [l for l in out.strip().split("\n") if l]
        expected = ["openclaw-admin", "chroma-uvmy-chromadb", "mcp-server", "ha-atlas"]
        for name in expected:
            if _container_up(lines, name):
                print(f"[OK] {name}")
            else:
                print(f"[WARN] {name} nicht Up oder fehlt")
                ok = False
        # Optionale VPS-Knoten (nur Hinweis, kein ok=False)
        for label, sub in [("evolution-api", "evolution"), ("monica", "monica"), ("kong", "kong")]:
            if _container_up(lines, sub):
                print(f"[OK] (optional) {label}")
            else:
                print(f"[--] (optional) {label} nicht gefunden")
        print(f"  Container gesamt: {len(lines)}")
        pc_ok, pc_msgs = verify_docker_ps_lines_tabbed(lines)
        for pm in pc_msgs:
            print(pm)
        if not pc_ok:
            ok = False
        k_ok, k_msg = _verify_kong_matches_deck_reference(lines)
        print(k_msg)
        if not k_ok:
            ok = False
        else:
            ph_ok, ph_msg = _verify_kong_proxy_health(lines)
            print(ph_msg)
            if not ph_ok:
                ok = False
    # 2) Chroma v2 heartbeat
    try:
        r = httpx.get(
            f"http://{VPS_HOST}:{CHROMA_PORT}/api/v2/heartbeat",
            timeout=15.0,
        )
        if r.status_code == 200 and "heartbeat" in r.text:
            print("[OK] Chroma v2 heartbeat")
        else:
            print("[FAIL] Chroma v2:", r.status_code, r.text[:200])
            ok = False
    except Exception as e:
        print("[FAIL] Chroma v2:", e)
        ok = False
    # 3) Optionale HTTP-Checks (Evolution, Monica, Kong) – nur Hinweis, kein Fail
    for url, kind in [
        (EVOLUTION_API_URL, "Evolution API"),
        (MONICA_URL, "Monica"),
        (KONG_ADMIN_URL, "Kong"),
    ]:
        try:
            u = url.strip().rstrip("/") or "http://localhost"
            r = httpx.get(u, timeout=3.0)
            if r.status_code in (200, 301, 302, 401, 404):
                print(f"[OK] (optional) {kind} erreichbar")
            else:
                print(f"[--] (optional) {kind} HTTP {r.status_code}")
        except Exception:
            print(f"[--] (optional) {kind} nicht erreichbar")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
