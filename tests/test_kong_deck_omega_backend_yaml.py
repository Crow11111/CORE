# -*- coding: utf-8 -*-
"""Deck-Referenz: omega-core-backend + /status — nur YAML-Parsing, kein Netz."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

_DECK = Path(__file__).resolve().parents[1] / "infra" / "vps" / "kong" / "kong-deck-reference.yaml"


def test_kong_deck_has_omega_core_backend_service_and_status_route() -> None:
    try:
        raw = _DECK.read_text(encoding="utf-8")
    except OSError as e:
        pytest.fail(f"Deck-Datei fehlt oder nicht lesbar: {_DECK} ({e})")
    data = yaml.safe_load(raw)
    assert isinstance(data, dict), "Deck-Root muss ein Mapping sein"
    services = data.get("services") or []
    routes = data.get("routes") or []
    snames = {s.get("name") for s in services if isinstance(s, dict)}
    assert "omega-core-backend" in snames, f"Service omega-core-backend fehlt: {snames!r}"
    rnames = {r.get("name") for r in routes if isinstance(r, dict)}
    assert "omega-core-status-route" in rnames, f"Route omega-core-status-route fehlt: {rnames!r}"
    status_route = next(
        (r for r in routes if isinstance(r, dict) and r.get("name") == "omega-core-status-route"),
        None,
    )
    assert status_route is not None
    assert status_route.get("service") == "omega-core-backend"
    paths = status_route.get("paths") or []
    assert "/status" in paths, f"/status in paths erwartet, got {paths!r}"
    assert status_route.get("strip_path") is False

    core_svc = next(
        (s for s in services if isinstance(s, dict) and s.get("name") == "omega-core-backend"),
        None,
    )
    assert core_svc is not None
    url = (core_svc.get("url") or "").lower()
    assert "172.17.0.1:32800" in url, f"Upstream-URL Soll docker-host:32800, Ist {url!r}"
