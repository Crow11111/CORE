#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gezielter Multi-View-Ingest für VPS-Playbook-Dokumente (wie ingest_core_documents).

Nutzt dieselbe Pipeline (`ingest_file` → `source_collection` = logischer CORE-Name).
Chroma-Facetten: fest in multi_view_client (mv_keywords / mv_semantics / mv_media).

Voraussetzung: Erreichbare Chroma-Instanz (CHROMA_HOST:CHROMA_PORT oder lokaler PersistentClient).
Ohne erreichbare Chroma-API: Exit 1 (kein simulierter Erfolg).

Remote Chroma nicht erreichbar: Operator mit laufendem Chroma / korrektem Tunnel ausführen.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(_PROJECT_ROOT / ".env", override=True)
    except ImportError:
        pass


def _preflight_chroma_or_exit() -> None:
    """Strikter Check: Chroma-HTTP oder Persistent-Pfad muss antworten."""
    import chromadb
    from chromadb.config import Settings

    host = (os.getenv("CHROMA_HOST") or "").strip()
    port_s = (os.getenv("CHROMA_PORT") or "8000").strip()
    try:
        port = int(port_s)
    except ValueError:
        print(f"[FAIL] CHROMA_PORT ungültig: {port_s!r}", file=sys.stderr)
        raise SystemExit(1)

    if host:
        import socket

        try:
            sock = socket.create_connection((host, port), timeout=6.0)
            sock.close()
        except OSError as exc:
            print(
                f"[FAIL] Chroma nicht erreichbar unter {host}:{port} ({exc}). "
                "Mit laufendem Chroma oder Tunnel erneut ausführen.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False),
        )
    else:
        from src.network.chroma_client import CHROMA_LOCAL_PATH

        client = chromadb.PersistentClient(
            path=CHROMA_LOCAL_PATH,
            settings=Settings(anonymized_telemetry=False),
        )

    try:
        client.list_collections()
    except Exception as exc:
        print(
            f"[FAIL] Chroma-API nicht nutzbar: {exc}. "
            "Instanz prüfen (Docker, Firewall, CHROMA_HOST/CHROMA_PORT).",
            file=sys.stderr,
        )
        raise SystemExit(1)


async def _run() -> int:
    from src.scripts.ingest_core_documents import ingest_file, vps_playbook_ingest_entries

    failed = 0
    for filepath, collection in vps_playbook_ingest_entries():
        p = Path(filepath)
        if not p.is_file():
            print(f"[FAIL] Datei fehlt: {p}", file=sys.stderr)
            failed += 1
            continue
        result = await ingest_file(str(p), collection)
        if result.get("failed", 0) > 0 or result.get("success", 0) < 1:
            print(f"[FAIL] Ingest unvollständig: {p} → {result}", file=sys.stderr)
            failed += 1
    return 1 if failed else 0


def main() -> int:
    _load_dotenv()
    _preflight_chroma_or_exit()
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
