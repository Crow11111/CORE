# -*- coding: utf-8 -*-
"""
VPS: Zero-Trust — veröffentlichte Host-Ports aus `docker ps` gegen `vps_public_ports.py`.

SSH-Ausgabezeilen (Tab-getrennt): Name, Status, Ports — siehe verify_vps_stack.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from src.config.vps_public_ports import (
    CHROMA_UVMY_HOST_PORT,
    EVOLUTION_API_HOST_PORT,
    HA_ATLAS_HOST_PORT,
    KONG_ADMIN_API_HOST_PORT,
    KONG_MANAGER_UI_HOST_PORT,
    KONG_PROXY_HOST_PORT,
    MCP_SERVER_HOST_PORT,
    MONICA_HTTP_HOST_PORT,
    OPENCLAW_ADMIN_HOST_PORT,
)

# IPv4 und IPv6-Bind-Muster auf dem Host
_HOST_PUBLISH_RE = re.compile(r"(?:0\.0\.0\.0|\:\:\:):(\d+)->")


def extract_published_host_ports(ports_field: str) -> set[int]:
    return {int(m) for m in _HOST_PUBLISH_RE.findall(ports_field or "")}


@dataclass(frozen=True)
class _PortRule:
    label: str
    match: Callable[[str], bool]
    required_ports: frozenset[int]


def _rules() -> tuple[_PortRule, ...]:
    return (
        _PortRule(
            "chroma-uvmy (chromadb)",
            lambda n: "chromadb" in n.lower() and "chroma" in n.lower(),
            frozenset({CHROMA_UVMY_HOST_PORT}),
        ),
        _PortRule(
            "kong proxy/admin/ui",
            lambda n: "kong" in n.lower() and "kong-" in n,
            frozenset(
                {
                    KONG_PROXY_HOST_PORT,
                    KONG_ADMIN_API_HOST_PORT,
                    KONG_MANAGER_UI_HOST_PORT,
                }
            ),
        ),
        _PortRule(
            "evolution-api",
            lambda n: "evolution-api" in n.lower(),
            frozenset({EVOLUTION_API_HOST_PORT}),
        ),
        _PortRule(
            "mcp-server",
            lambda n: n.strip() == "mcp-server" or n.startswith("mcp-server"),
            frozenset({MCP_SERVER_HOST_PORT}),
        ),
        _PortRule(
            "openclaw-admin",
            lambda n: "openclaw-admin" in n,
            frozenset({OPENCLAW_ADMIN_HOST_PORT}),
        ),
        _PortRule(
            "ha-atlas",
            lambda n: "ha-atlas" in n,
            frozenset({HA_ATLAS_HOST_PORT}),
        ),
        _PortRule(
            "monica",
            lambda n: "monica" in n.lower()
            and ("monica-" in n.lower() or n.lower().startswith("monica")),
            frozenset({MONICA_HTTP_HOST_PORT}),
        ),
    )


def verify_docker_ps_lines_tabbed(lines: list[str]) -> tuple[bool, list[str]]:
    """
    Jede Zeile: Name\\tStatus\\tPorts (docker ps --format).
    Nur Zeilen, deren Container laut Status „Up“ ist und die eine Regel matchen, werden geprüft.
    """
    messages: list[str] = []
    ok = True
    rules = _rules()

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split("\t", 2)
        if len(parts) < 2:
            continue
        name, status = parts[0], parts[1]
        ports_field = parts[2] if len(parts) > 2 else ""
        if "Up" not in status:
            continue
        published = extract_published_host_ports(ports_field)
        for rule in rules:
            if not rule.match(name):
                continue
            missing = rule.required_ports - published
            if missing:
                ok = False
                messages.append(
                    f"[FAIL] {rule.label} Container `{name}`: "
                    f"fehlende Host-Ports {sorted(missing)} (Vertrag); "
                    f"gefunden {sorted(published)}"
                )
            else:
                messages.append(
                    f"[OK] {rule.label} `{name}`: Ports {sorted(rule.required_ports)} gemappt"
                )
            break

    return ok, messages


def main() -> int:
    import os
    import subprocess
    import sys
    from pathlib import Path

    from dotenv import load_dotenv

    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env", override=True)
    vps = os.getenv("VPS_HOST", "127.0.0.1")
    key = os.getenv("VPS_SSH_KEY", "")
    if not key or vps in ("127.0.0.1", "localhost"):
        print("[--] VPS_HOST nicht gesetzt oder lokal — Port-Contract-SSH übersprungen")
        return 0
    cmd = (
        f'ssh -o ConnectTimeout=15 -o BatchMode=yes -i "{key}" '
        f'root@{vps} "docker ps --format \'{{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}\'"'
    )
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=45)
    if r.returncode != 0:
        out = ((r.stdout or "") + (r.stderr or ""))[:400]
        print("[FAIL] SSH/docker ps:", out)
        return 1
    lines = [l for l in r.stdout.strip().split("\n") if l]
    good, msgs = verify_docker_ps_lines_tabbed(lines)
    for m in msgs:
        print(m)
    if not good:
        return 1
    if not msgs:
        print("[WARN] Keine Vertrags-Container mit passenden Namen in docker ps gefunden")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
