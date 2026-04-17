# -*- coding: utf-8 -*-
"""Kontrakt: vps_kong_ensure_omega_core_backend — httpx gemockt (kein Netz, kein Import-Heroin)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _resp(
    status_code: int,
    json_body: dict | None = None,
    text: str = "",
) -> MagicMock:
    m = MagicMock()
    m.status_code = status_code
    m.text = text or ""
    if json_body is not None:
        m.json.return_value = json_body
    return m


@patch("src.scripts.vps_kong_ensure_omega_core_backend.httpx.post")
@patch("src.scripts.vps_kong_ensure_omega_core_backend.httpx.get")
def test_posts_service_and_route_when_both_missing(mock_get: MagicMock, mock_post: MagicMock) -> None:
    def get_side_effect(url: str, **kwargs: object) -> MagicMock:
        if url.rstrip("/").endswith("/services"):
            return _resp(200, {"data": []})
        if url.rstrip("/").endswith("/routes"):
            return _resp(200, {"data": []})
        pytest.fail(f"Unerwarteter GET {url!r}")

    mock_get.side_effect = get_side_effect
    mock_post.side_effect = [_resp(201, {}), _resp(201, {})]

    try:
        from src.scripts.vps_kong_ensure_omega_core_backend import main
    except ImportError as e:
        pytest.fail(f"Modul/Funktion fehlt noch. TDD-Kontrakt nicht erfüllt: {e}")

    assert main() == 0
    assert mock_post.call_count == 2
    svc_call = mock_post.call_args_list[0]
    assert svc_call[0][0].rstrip("/").endswith("/services")
    assert svc_call[1]["json"]["name"] == "omega-core-backend"
    assert "172.17.0.1" in svc_call[1]["json"]["url"]
    route_call = mock_post.call_args_list[1]
    assert "/services/omega-core-backend/routes" in route_call[0][0]
    assert route_call[1]["json"]["name"] == "omega-core-status-route"
    assert route_call[1]["json"]["paths"] == ["/status"]
    assert route_call[1]["json"]["strip_path"] is False
    assert route_call[1]["json"]["protocols"] == ["http", "https"]


@patch("src.scripts.vps_kong_ensure_omega_core_backend.httpx.post")
@patch("src.scripts.vps_kong_ensure_omega_core_backend.httpx.get")
def test_no_post_when_service_and_route_present(mock_get: MagicMock, mock_post: MagicMock) -> None:
    def get_side_effect(url: str, **kwargs: object) -> MagicMock:
        if url.rstrip("/").endswith("/services"):
            return _resp(
                200,
                {"data": [{"name": "omega-core-backend", "id": "svc-1"}]},
            )
        if url.rstrip("/").endswith("/routes"):
            return _resp(
                200,
                {
                    "data": [
                        {
                            "name": "omega-core-status-route",
                            "paths": ["/status"],
                        }
                    ]
                },
            )
        pytest.fail(f"Unerwarteter GET {url!r}")

    mock_get.side_effect = get_side_effect

    try:
        from src.scripts.vps_kong_ensure_omega_core_backend import main
    except ImportError as e:
        pytest.fail(f"Modul/Funktion fehlt noch. TDD-Kontrakt nicht erfüllt: {e}")

    assert main() == 0
    mock_post.assert_not_called()


@patch("src.scripts.vps_kong_ensure_omega_core_backend.httpx.post")
@patch("src.scripts.vps_kong_ensure_omega_core_backend.httpx.get")
def test_only_route_post_when_service_exists(mock_get: MagicMock, mock_post: MagicMock) -> None:
    def get_side_effect(url: str, **kwargs: object) -> MagicMock:
        if url.rstrip("/").endswith("/services"):
            return _resp(
                200,
                {"data": [{"name": "omega-core-backend", "id": "svc-1"}]},
            )
        if url.rstrip("/").endswith("/routes"):
            return _resp(200, {"data": []})
        pytest.fail(f"Unerwarteter GET {url!r}")

    mock_get.side_effect = get_side_effect
    mock_post.side_effect = [_resp(201, {})]

    try:
        from src.scripts.vps_kong_ensure_omega_core_backend import main
    except ImportError as e:
        pytest.fail(f"Modul/Funktion fehlt noch. TDD-Kontrakt nicht erfüllt: {e}")

    assert main() == 0
    assert mock_post.call_count == 1
    assert "/services/omega-core-backend/routes" in mock_post.call_args[0][0]
