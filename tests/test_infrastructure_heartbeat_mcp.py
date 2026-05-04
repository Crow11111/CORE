# -*- coding: utf-8 -*-
"""Sentinel: VPS mcp-server Erreichbarkeit (TCP Port check)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from loguru import logger


@pytest.mark.asyncio
async def test_check_tcp_port_up_true_on_success():
    logger.debug("Testing TCP port up on success")
    mod = __import__("src.services.infrastructure_heartbeat", fromlist=["*"])
    s = mod.InfrastructureSentinel()

    mock_reader = MagicMock()
    mock_writer = MagicMock()
    mock_writer.wait_closed = AsyncMock()

    with patch.object(asyncio, "open_connection", AsyncMock(return_value=(mock_reader, mock_writer))):
        ok = await s.check_tcp_port_up("example.test", 8001)
    
    assert ok is True
    mock_writer.close.assert_called_once()
    mock_writer.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_tcp_port_up_false_on_connection_error():
    logger.debug("Testing TCP port down on connection error")
    mod = __import__("src.services.infrastructure_heartbeat", fromlist=["*"])
    s = mod.InfrastructureSentinel()

    with patch.object(asyncio, "open_connection", AsyncMock(side_effect=OSError("refused"))):
        ok = await s.check_tcp_port_up("127.0.0.1", 59999)
    assert ok is False
