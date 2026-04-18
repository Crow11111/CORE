# -*- coding: utf-8 -*-
"""Sentinel: VPS mcp-server Erreichbarkeit (HTTP any-response)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from loguru import logger


@pytest.mark.asyncio
async def test_check_http_server_up_true_on_404_response():
    logger.debug("Testing HTTP server up on 404")
    mod = __import__("src.services.infrastructure_heartbeat", fromlist=["*"])
    s = mod.InfrastructureSentinel()

    class _Resp:
        status_code = 404

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, **kwargs):
            logger.success("Mock GET call triggered (404 scenario)")
            return _Resp()

    with patch.object(mod.httpx, "AsyncClient", MagicMock(return_value=_Client())):
        ok = await s.check_http_server_up("http://example.test:8001/")
    assert ok is True


@pytest.mark.asyncio
async def test_check_http_server_up_false_on_connection_error():
    logger.debug("Testing HTTP server down on connection error")
    mod = __import__("src.services.infrastructure_heartbeat", fromlist=["*"])
    s = mod.InfrastructureSentinel()

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, **kwargs):
            logger.success("Mock GET call triggered (Error scenario)")
            raise OSError("refused")

    with patch.object(mod.httpx, "AsyncClient", MagicMock(return_value=_Client())):
        ok = await s.check_http_server_up("http://127.0.0.1:59999/")
    assert ok is False
