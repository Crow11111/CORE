# -*- coding: utf-8 -*-
"""
Kontrakt-Tests für omega_events / event_store_client (TICKET 11 Phase 1).

Verification-First: Mockt _run_pg_sql — Fehlschlag durch Assertions, nicht durch ImportError.
"""
from __future__ import annotations

import json
import re
from unittest.mock import AsyncMock, patch

import pytest


def _load_event_store():
    try:
        return __import__("src.db.event_store_client", fromlist=["*"])
    except ImportError as exc:
        pytest.fail(
            f"TICKET 11 Phase 1: event_store_client fehlt. TDD-Kontrakt nicht erfüllt. ({exc})"
        )


@pytest.mark.asyncio
async def test_record_event_calls_pg_with_insert_and_required_memory_hash():
    mod = _load_event_store()
    if not hasattr(mod, "record_event"):
        pytest.fail(
            "Zero-Trust / TICKET 11: record_event fehlt — episodische Persistenz ohne Audit-Pfad."
        )

    captured: list[tuple[bool, str]] = []

    async def fake_run(sql: str, timeout: int = 30):
        captured.append((True, sql))
        return True, " ok "

    with patch.object(mod, "_run_pg_sql", new=AsyncMock(side_effect=fake_run)):
        result = await mod.record_event(
            agent_id="agent-alpha",
            event_type="preflight_ack",
            content={"phase": 1},
            memory_hash="sha256:deadbeef",
        )

    assert isinstance(result, dict), "record_event muss strukturiertes Dict liefern (A7)."
    assert result.get("success") is True, result
    assert len(captured) == 1
    sql = captured[0][1]
    assert "INSERT INTO omega_events" in sql
    assert "agent-alpha" in sql
    assert "preflight_ack" in sql
    assert "sha256:deadbeef" in sql
    assert "memory_hash" in sql.lower() or "sha256:deadbeef" in sql


@pytest.mark.asyncio
async def test_record_event_rejects_empty_memory_hash():
    mod = _load_event_store()
    result = await mod.record_event(
        agent_id="a",
        event_type="t",
        content={},
        memory_hash="",
    )
    assert result.get("success") is False
    assert "memory_hash" in (result.get("error") or "").lower()


@pytest.mark.asyncio
async def test_get_history_parses_json_aggregate():
    mod = _load_event_store()
    if not hasattr(mod, "get_history"):
        pytest.fail(
            "TICKET 11 Pre-Flight-Pfad: get_history fehlt — keine chronologische Abfrage."
        )

    payload = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2026-04-03T12:00:00+00:00",
            "agent_id": "x",
            "event_type": "e",
            "content": {"k": 1},
            "memory_hash": "h1",
        }
    ]
    raw = json.dumps(payload)

    async def fake_run(sql: str, timeout: int = 30):
        assert "FROM omega_events" in sql
        assert "ORDER BY" in sql.upper()
        return True, raw + "\n(1 row)\n"

    with patch.object(mod, "_run_pg_sql", new=AsyncMock(side_effect=fake_run)):
        rows = await mod.get_history(agent_id=None, limit=10)

    assert len(rows) == 1
    assert rows[0]["agent_id"] == "x"
    assert rows[0]["memory_hash"] == "h1"
    assert rows[0]["content"] == {"k": 1}


@pytest.mark.asyncio
async def test_get_history_sanitizes_limit_int():
    mod = _load_event_store()

    async def fake_run(sql: str, timeout: int = 30):
        m = re.search(r"LIMIT\s+(\d+)", sql, re.I)
        assert m, f"LIMIT muss Integer sein, SQL-Ausschnitt: {sql[:200]}"
        assert int(m.group(1)) <= 1000
        return True, "[]"

    with patch.object(mod, "_run_pg_sql", new=AsyncMock(side_effect=fake_run)):
        await mod.get_history(limit=999999)
