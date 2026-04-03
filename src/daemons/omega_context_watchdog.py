# -*- coding: utf-8 -*-
"""
OMEGA Context Watchdog — TICKET 11 Phase 3 (Context Forcing).

Pollt die juengste Event-Historie und schreibt sie in eine Markdown-Statusdatei
fuer Cursor-Kontext (Attention Dilution ↓).
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

DEFAULT_CURSOR_STATUS_PATH = "docs/05_AUDIT_PLANNING/cursor_status.md"

CONTEXT_HEADER = "OMEGA CONTEXT FORCING - ACTIVE MEMORY"


def _format_events_markdown(events: list[dict[str, Any]]) -> str:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    lines: list[str] = [
        f"# {CONTEXT_HEADER}",
        "",
        f"_Updated (UTC): {now}_",
        "",
        "## Latest events (newest first)",
        "",
    ]
    for i, ev in enumerate(events, start=1):
        et = ev.get("event_type", "")
        aid = ev.get("agent_id", "")
        lines.append(f"### {i}. `{et}` — `{aid}`")
        lines.append("")
        lines.append(f"- **id:** `{ev.get('id', '')}`")
        lines.append(f"- **timestamp:** `{ev.get('timestamp', '')}`")
        lines.append(f"- **memory_hash:** `{ev.get('memory_hash', '')}`")
        content = ev.get("content", {})
        pj = json.dumps(content, ensure_ascii=False, indent=2)
        lines.append("- **content:**")
        lines.append("")
        lines.append("```json")
        lines.append(pj)
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _atomic_write_text(path: str | Path, text: str) -> None:
    """Schreibt vollstaendigen Inhalt per temp + replace (POSIX: atomar im selben FS)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(text.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, p)
    except BaseException:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


async def inject_latest_context(
    file_path: str = DEFAULT_CURSOR_STATUS_PATH,
) -> None:
    # Lazy import: Tests koennen src.db.event_store_client.get_history mocken.
    from src.db import event_store_client

    rows = await event_store_client.get_history(limit=5)
    body = _format_events_markdown(rows)
    _atomic_write_text(file_path, body)


async def run_watchdog(
    interval: float = 10.0,
    file_path: str = DEFAULT_CURSOR_STATUS_PATH,
    *,
    inject_fn: Callable[[str], Awaitable[None]] | None = None,
    sleep_fn: Callable[[float], Awaitable[None]] | None = None,
    stop_event: asyncio.Event | None = None,
) -> None:
    """
    Periodische Injektion. Ueber inject_fn / sleep_fn / stop_event im Test isolierbar.
    """
    inject = inject_fn if inject_fn is not None else inject_latest_context
    sleep = sleep_fn if sleep_fn is not None else asyncio.sleep
    stop = stop_event if stop_event is not None else asyncio.Event()

    while not stop.is_set():
        await inject(file_path)
        await sleep(interval)
