# -*- coding: utf-8 -*-
"""
Kontrakt-Tests: Context-Forcing Watchdog (TICKET 11 Phase 3).

Verification-First: Mockt get_history — Fehlschlag über Assertions, nicht ImportError.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


def _load_watchdog():
    try:
        return __import__(
            "src.daemons.omega_context_watchdog", fromlist=["*"]
        )
    except ImportError as exc:
        pytest.fail(
            f"TICKET 11 Phase 3: omega_context_watchdog fehlt. TDD-Kontrakt nicht erfüllt. ({exc})"
        )


@pytest.mark.asyncio
async def test_inject_latest_context_writes_markdown_with_header_and_events(tmp_path):
    mod = _load_watchdog()
    if not hasattr(mod, "inject_latest_context"):
        pytest.fail(
            "Context Forcing: inject_latest_context fehlt — keine dynamische Status-Injektion."
        )

    two_events = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "timestamp": "2026-04-03T10:00:00+00:00",
            "agent_id": "agent-a",
            "event_type": "lesson_learned",
            "content": {"note": "keep hash"},
            "memory_hash": "sha256:aaa",
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "timestamp": "2026-04-03T11:00:00+00:00",
            "agent_id": "agent-b",
            "event_type": "preflight_ack",
            "content": {"ok": True},
            "memory_hash": "sha256:bbb",
        },
    ]

    mock_get_history = AsyncMock(return_value=two_events)

    out_file = tmp_path / "cursor_status.md"
    with patch(
        "src.db.event_store_client.get_history", new=mock_get_history
    ):
        await mod.inject_latest_context(str(out_file))

    mock_get_history.assert_awaited_once_with(limit=5)

    text = out_file.read_text(encoding="utf-8")
    assert "OMEGA CONTEXT FORCING - ACTIVE MEMORY" in text, (
        "Sichtbarer Header fuer Cursor-Kontext fehlt."
    )
    assert "lesson_learned" in text and "preflight_ack" in text, text
    assert "sha256:aaa" in text and "sha256:bbb" in text, text
    assert "keep hash" in text, text
    assert "11111111-1111-1111-1111-111111111111" in text, text
    assert "22222222-2222-2222-2222-222222222222" in text, text


@pytest.mark.asyncio
async def test_run_watchdog_calls_inject_until_stop(tmp_path):
    mod = _load_watchdog()
    if not hasattr(mod, "run_watchdog"):
        pytest.fail("Context Forcing: run_watchdog fehlt — kein periodischer Pfad testbar.")

    stop = asyncio.Event()
    calls: list[str] = []

    async def fake_inject(path: str) -> None:
        calls.append(path)
        if len(calls) >= 2:
            stop.set()

    async def no_sleep(_interval: float) -> None:
        await asyncio.sleep(0)
        _ = _interval + 0.0
        return None

    p = str(tmp_path / "status.md")
    await mod.run_watchdog(
        interval=999.0,
        file_path=p,
        inject_fn=fake_inject,
        sleep_fn=no_sleep,
        stop_event=stop,
    )

    assert calls == [p, p], f"Erwartet genau zwei Injektionen vor Stop, got {calls!r}"


@pytest.mark.asyncio
async def test_default_file_path_constant_points_under_audit_planning():
    mod = _load_watchdog()
    expected_suffix = "docs/05_AUDIT_PLANNING/cursor_status.md"
    default = getattr(mod, "DEFAULT_CURSOR_STATUS_PATH", None)
    if default is None:
        pytest.fail("DEFAULT_CURSOR_STATUS_PATH fehlt — Default-Pfad nicht dokumentiert.")
    assert str(default).replace("\\", "/").endswith(expected_suffix), default
