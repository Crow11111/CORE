# -*- coding: utf-8 -*-
"""
OMEGA STATE MCP Server — optional: Proxy zu localhost:8049 (nur Dev-Workstation).

- **8049 / state_mtls_proxy:** Relais für `read_core_state` / `read_handbook` → HTTPS+mTLS zum VPS
  (`/core_api/...`). Läuft auf dem Rechner, auf dem Cursor den MCP startet — **nicht** auf dem VPS.
- **InfrastructureSentinel** (`infrastructure_heartbeat.py`) prüft **kein** 127.0.0.1; nur VPS/Scout/Dreadnought-sichtbare Endpunkte.
- **get_orchestrator_bootstrap:** Testet 8049 **nur** wenn `OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1` (Default: aus),
  damit keine falsche „Heartbeat-gegen-local“-Semantik entsteht.
- **query_canon_semantic:** Semantische Abfrage **`core_canon`** (Soll-Kanon / Anker-Registry-Ingest).
- **query_operational_semantic:** Semantische Abfrage **`core_operational`** (Ist / Lauffläche laut `KERNARBEITER_SURFACE_PATHS.yaml`).
  Parallel: **`query_chromadb`** (`core-chromadb`) mit passendem `collection_name`.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import httpx

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from mcp.server.fastmcp import FastMCP

from src.config.chroma_zero_trust_notice import CHROMA_ZERO_TRUST_NOTICE
from src.config.vps_public_ports import MCP_SERVER_HOST_PORT as _VPS_MCP_HOST_PORT
from src.db import event_store_client as _omega_event_store

mcp = FastMCP("OMEGA_STATE_NEXUS")
PROXY_URL = "http://localhost:8049"

_HANDBOOKS_DIR = Path(_REPO) / "docs" / "03_INFRASTRUCTURE" / "handbooks"
_ROLE_SAFE = re.compile(r"^[\w.-]+$")


def _env_bootstrap_probe_local_proxy() -> bool:
    v = (os.getenv("OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _handbook_file_for_role(role: str) -> Path:
    r = (role or "").strip()
    if not r or not _ROLE_SAFE.match(r):
        raise ValueError(f"ungültiger handbook role (nur [A-Za-z0-9_.-]): {role!r}")
    return _HANDBOOKS_DIR / f"{r}.md"


def _read_handbook_local(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _atomic_write_handbook(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parent = path.parent
    fd, tmp_name = tempfile.mkstemp(prefix=".hb-", suffix=".tmp", dir=str(parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tf:
            tf.write(content)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


@mcp.tool()
async def read_core_state() -> str:
    """
    Liest den aktuellen 4D CORE State Vector (S * P Symbiose) vom VPS via Proxy.
    Jeder Sub-Agent sollte dies als erstes tun, um seine physikalische/logische Dichte zu messen.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{PROXY_URL}/state")
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": (
                "Kein HTTP-Dienst auf localhost:8049 (Sync-Relay/mTLS-State-Proxy). "
                "Typisch: `state_mtls_proxy` / zugehöriger Daemon ist nicht gestartet — "
                "nicht automatisch „VPS offline“."
            ),
        })

@mcp.tool()
async def read_handbook(role: str) -> str:
    """
    Liest das persistente Gedächtnis (Handbuch) für eine spezifische Rolle (z.B. 'system-architect') vom VPS via Proxy.
    Fallback: Datei `docs/03_INFRASTRUCTURE/handbooks/{role}.md` wenn localhost:8049 nicht erreichbar.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{PROXY_URL}/handbook/{role}")
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        try:
            p = _handbook_file_for_role(role)
        except ValueError as ve:
            return f"Proxy-Fehler: {e} | {ve}"
        if not p.is_file():
            return (
                f"Fehler beim Lesen des Handbuchs via Proxy: {e}\n"
                f"Kein lokaler Fallback: {p} fehlt."
            )
        return await asyncio.to_thread(_read_handbook_local, p)

@mcp.tool()
async def update_handbook(role: str, content: str) -> str:
    """
    Überschreibt das persistente Gedächtnis (Handbuch) für die angegebene Rolle auf dem VPS.
    PFLICHT für jeden Sub-Agenten vor seiner Terminierung, falls neue Erkenntnisse gewonnen wurden.
    Fallback: atomar nach `docs/03_INFRASTRUCTURE/handbooks/{role}.md` wenn Proxy down.
    """
    try:
        async with httpx.AsyncClient() as client:
            payload = {"content": content, "reason": "MCP-Update"}
            resp = await client.post(f"{PROXY_URL}/handbook/{role}", json=payload)
            resp.raise_for_status()
            return f"[SUCCESS] Handbuch für {role} wurde via Proxy erfolgreich aktualisiert."
    except Exception:
        try:
            p = _handbook_file_for_role(role)
        except ValueError as ve:
            return f"[FAIL] Proxy down und ungültige Rolle: {ve}"
        try:
            await asyncio.to_thread(_atomic_write_handbook, p, content)
            return (
                f"[SUCCESS] lokal (Fallback, Proxy down) — {p}"
            )
        except Exception as e2:
            return f"[FAIL] Proxy und lokaler Fallback: {e2}"


def _canon_summary_row(row: dict) -> dict:
    return {
        "repo_path": row.get("repo_path"),
        "document_role": row.get("document_role"),
        "anchor_section": row.get("anchor_section"),
        "last_synced_at": row.get("last_synced_at"),
    }


def _event_summary_row(row: dict) -> dict:
    c = row.get("content") or {}
    if isinstance(c, dict):
        summ = (c.get("summary") or c.get("task_hint") or str(c)[:120])[:200]
    else:
        summ = str(c)[:200]
    return {
        "timestamp": row.get("timestamp"),
        "event_type": row.get("event_type"),
        "agent_id": row.get("agent_id"),
        "summary": summ,
    }


async def _probe_vps_mcp_http() -> bool | None:
    host = (os.getenv("VPS_HOST") or "").strip()
    if not host:
        return None
    url = f"http://{host}:{_VPS_MCP_HOST_PORT}/"
    try:
        async with httpx.AsyncClient(verify=False, timeout=4.0) as client:
            await client.get(url)
            return True
    except Exception:
        return False


async def _probe_local_state_proxy() -> bool | None:
    """
    Nur Dev-Workstation. Default: None (nicht geprüft) — siehe Modul-Docstring.
    """
    if not _env_bootstrap_probe_local_proxy():
        return None
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get(f"{PROXY_URL}/state")
            return r.status_code < 500
    except Exception:
        return False


def _gaps_and_recommendations(
    canon_rows: list,
    event_rows: list,
    vps_mcp: bool | None,
    proxy_ok: bool | None,
    task_hint: str,
) -> tuple[list[str], list[str]]:
    gaps: list[str] = []
    rec: list[str] = []
    if not canon_rows:
        gaps.append(
            "omega_canon_documents leer oder PostgreSQL nicht erreichbar — Kanon-Index fehlt."
        )
        rec.append("Ausführen: `python -m src.scripts.sync_omega_canon_registry`")
    if not event_rows:
        gaps.append(
            "omega_events (letzte Abfrage) leer — kein episodisches Audit-Fenster für diese Session."
        )
        rec.append("Abschluss von Tasks: `record_event` mit gültigem memory_hash.")
    if vps_mcp is False:
        gaps.append(
            f"VPS-Host MCP-HTTP (Port {_VPS_MCP_HOST_PORT}) nicht erreichbar — Remote-Tooling ggf. down."
        )
        rec.append("Prüfen: `verify_vps_stack`, Docker `mcp-server`, UFW.")
    if proxy_ok is False:
        gaps.append(
            "Dev-Workstation: localhost:8049 (state_mtls_proxy) nicht erreichbar — read_core_state/read_handbook ohne VPS-mTLS-Relais."
        )
        rec.append("Start: `docs/04_PROCESSES/STATE_MTLS_PROXY_START.md` (nur lokal, nicht VPS-Heartbeat).")
    th = (task_hint or "").lower()
    if "kong" in th:
        rec.append("Kontext: `infra/vps/kong/kong-deck-reference.md`, `vps_kong_ensure_omega_core_backend`")
    if "omega-backend" in th or "32800" in th:
        rec.append("Kontext: `docs/03_INFRASTRUCTURE/OMEGA_BACKEND_VPS_SYSTEMD.md`")
    if "chrom" in th:
        rec.append("Kontext: `VPS_HOST_PORT_CONTRACT.md` Chroma 32779")
    return gaps, rec


@mcp.tool()
async def get_orchestrator_bootstrap(
    event_limit: int = 12,
    canon_limit: int = 80,
    task_hint: str = "",
) -> str:
    """
    Ein Aufruf für Orchestrator/Producer: Kanon-Kurzliste + letzte Events + Erreichbarkeit
    (VPS-MCP-HTTP auf dem Host) + optional 8049 nur bei Env `OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1`
    + Lücken + Empfehlungen. Basis-Projektinfo ohne volles Repo zu lesen.
    """
    if isinstance(event_limit, bool) or not isinstance(event_limit, int):
        event_limit = 12
    if isinstance(canon_limit, bool) or not isinstance(canon_limit, int):
        canon_limit = 80
    event_limit = max(1, min(event_limit, 100))
    canon_limit = max(1, min(canon_limit, 300))

    canon_full = await _omega_event_store.list_canon_documents(limit=canon_limit)
    events_full = await _omega_event_store.get_history(agent_id=None, limit=event_limit)

    vps_mcp = await _probe_vps_mcp_http()
    proxy_ok = await _probe_local_state_proxy()

    gaps, recommendations = _gaps_and_recommendations(
        canon_full,
        events_full,
        vps_mcp,
        proxy_ok,
        task_hint,
    )

    bundle = {
        "canon_documents_summary": [_canon_summary_row(r) for r in canon_full],
        "canon_count": len(canon_full),
        "recent_events_summary": [_event_summary_row(r) for r in events_full],
        "events_count": len(events_full),
        "local_proxy_probe_enabled": _env_bootstrap_probe_local_proxy(),
        "reachability": {
            "vps_mcp_http": vps_mcp,
            "dev_workstation_state_proxy_8049": proxy_ok,
        },
        "reachability_notes": [
            "vps_mcp_http = HTTP auf VPS-Host-Port (Docker mcp-server), nicht der Cursor-stdio-MCP-Prozess.",
            "dev_workstation_state_proxy_8049 = nur wenn OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1; sonst null (unbekannt). Kein Bestandteil des InfrastructureSentinel.",
        ],
        "gaps": gaps,
        "recommendations": recommendations,
        "static_pointers": [
            "OMEGA_RESONANCE_ANCHOR.md",
            "KANON_EINSTIEG.md",
            "docs/02_ARCHITECTURE/KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md",
            "docs/04_PROCESSES/CANON_REGISTRY_AGENT_BINDUNG.md",
            "docs/04_PROCESSES/STATE_MTLS_PROXY_START.md",
            "docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md",
            "MCP: query_canon_semantic (Soll) + query_operational_semantic (Ist)",
        ],
        "task_hint_received": (task_hint or "").strip()[:500],
    }
    return json.dumps(bundle, ensure_ascii=False, default=str)


async def _chroma_semantic_query(
    *,
    collection: str,
    query_text: str,
    n_results: int,
    ingest_hint: str,
    missing_hint: str,
) -> str:
    from src.network.chroma_client import _get_collection_sync, is_configured

    q = (query_text or "").strip()
    if not q:
        return json.dumps(
            {"error": "query_text leer", "zero_trust_notice": _CHROMA_ZERO_TRUST_NOTICE},
            ensure_ascii=False,
        )

    if not is_configured():
        return json.dumps(
            {
                "error": "ChromaDB nicht konfiguriert (CHROMA_HOST oder CHROMA_LOCAL_PATH).",
                "collection": collection,
                "hint": ingest_hint,
                "zero_trust_notice": CHROMA_ZERO_TRUST_NOTICE,
            },
            ensure_ascii=False,
        )

    if isinstance(n_results, bool) or not isinstance(n_results, int):
        n_results = 8
    n = max(1, min(n_results, 25))

    def _run_query():
        col = _get_collection_sync(collection, create_if_missing=False)
        return col.query(query_texts=[q], n_results=n)

    try:
        result = await asyncio.to_thread(_run_query)
    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "collection": collection,
                "hint": missing_hint,
                "zero_trust_notice": CHROMA_ZERO_TRUST_NOTICE,
            },
            ensure_ascii=False,
        )

    out = dict(result) if isinstance(result, dict) else {"raw": result}
    out["collection"] = collection
    out["query_text"] = q[:500]
    out["zero_trust_notice"] = CHROMA_ZERO_TRUST_NOTICE
    return json.dumps(out, ensure_ascii=False, default=str)


@mcp.tool()
async def query_canon_semantic(query_text: str, n_results: int = 8) -> str:
    """
    Semantisches **Soll-Kanon**-Gedächtnis: Chroma **`core_canon`** (`omega_canon_documents` / Anker-Ingest).

    Ingest: `python -m src.scripts.ingest_omega_canon_chroma` nach PG-Sync.

    **Zero-Trust:** JSON enthält immer `zero_trust_notice` — Treffer sind keine Fakten ohne Abgleich mit Quelldatei.
    """
    from src.network.chroma_client import COLLECTION_CORE_CANON

    return await _chroma_semantic_query(
        collection=COLLECTION_CORE_CANON,
        query_text=query_text,
        n_results=n_results,
        ingest_hint="Ingest: python -m src.scripts.ingest_omega_canon_chroma — CANON_REGISTRY_AGENT_BINDUNG.md §5",
        missing_hint="Collection leer/fehlt? create_chroma_collections_vps + ingest_omega_canon_chroma.",
    )


@mcp.tool()
async def query_operational_semantic(query_text: str, n_results: int = 8) -> str:
    """
    Semantisches **Ist-/Laufflächen**-Gedächtnis: Chroma **`core_operational`**
    (Ports, Kong, Knoten, Messbarkeit — kuratiert via `KERNARBEITER_SURFACE_PATHS.yaml`).

    Ingest: `python -m src.scripts.ingest_omega_operational_chroma`.
    Orientierung: `docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md`.

    **Zero-Trust:** JSON enthält immer `zero_trust_notice` — auch Ist-Doku kann veraltet sein; Live-Checks wo nötig.
    """
    from src.network.chroma_client import COLLECTION_CORE_OPERATIONAL

    return await _chroma_semantic_query(
        collection=COLLECTION_CORE_OPERATIONAL,
        query_text=query_text,
        n_results=n_results,
        ingest_hint="Ingest: python -m src.scripts.ingest_omega_operational_chroma",
        missing_hint="Collection leer/fehlt? create_chroma_collections_vps + ingest_omega_operational_chroma.",
    )


@mcp.tool()
async def list_canon_documents(limit: int = 200) -> str:
    """
    PostgreSQL omega_canon_documents: registrierte Kanon-Pfade (Resonanz-Anker + Sync).
    Pre-Flight vor größeren Architektur-/VPS-/Kong-Aufgaben — gleicher PG-Pfad wie omega_events.
    """
    if isinstance(limit, bool) or not isinstance(limit, int):
        limit = 200
    rows = await _omega_event_store.list_canon_documents(limit=limit)
    return json.dumps(
        {
            "documents": rows,
            "count": len(rows),
            "hint": "Quelle: python -m src.scripts.sync_omega_canon_registry; Plan: MIGRATIONPLAN_OMEGA_WISSEN_DBS.md",
        },
        ensure_ascii=False,
        default=str,
    )


@mcp.tool()
async def get_episodic_history(agent_id: str | None = None, limit: int = 100) -> str:
    """
    Liefert die chronologische Event-Historie aus PostgreSQL (omega_events) für Pre-Flight /
    Episodisches Gedächtnis. Delegiert nicht an den 8049-Proxy — direkter PG-Pfad (TICKET 11).
    """
    if isinstance(limit, bool) or not isinstance(limit, int):
        limit = 100
    rows = await _omega_event_store.get_history(agent_id=agent_id, limit=limit)
    return json.dumps(
        {"events": rows, "count": len(rows)},
        ensure_ascii=False,
        default=str,
    )


@mcp.tool()
async def record_event(agent_id: str, event_type: str, content_json: str, memory_hash: str) -> str:
    """
    Schreibt ein append-only Event in omega_events (Abschluss / Audit). content_json muss
    gültiges JSON sein; memory_hash ist Pflicht (Zero-Trust).
    """
    raw = (content_json or "").strip()
    if not raw:
        raw = "{}"
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as e:
        return json.dumps(
            {
                "success": False,
                "id": None,
                "error": f"content_json parse error: {e}",
            },
            ensure_ascii=False,
        )
    if not isinstance(body, dict):
        body = {"payload": body}
    result = await _omega_event_store.record_event(
        agent_id=agent_id,
        event_type=event_type,
        content=body,
        memory_hash=memory_hash,
    )
    return json.dumps(result, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
