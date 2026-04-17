# -*- coding: utf-8 -*-
"""core_operational Ingest: YAML → Rows, dry-run, gemocktes Chroma."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "docs" / "00_STAMMDOKUMENTE" / "KERNARBEITER_SURFACE_PATHS.yaml"


def test_load_surface_rows_reads_yaml() -> None:
    from src.scripts import ingest_omega_operational_chroma as mod

    rows = mod.load_surface_rows(YAML_PATH)
    assert len(rows) >= 10
    paths = {r["repo_path"] for r in rows}
    assert "KANON_EINSTIEG.md" in paths
    assert "docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md" in paths
    assert all(r.get("document_role") == "operational_surface" for r in rows)


def test_stable_operational_chunk_id() -> None:
    from src.scripts import ingest_omega_operational_chroma as mod

    a = mod.stable_operational_chunk_id("x.md", 0)
    assert a.startswith("co_")
    assert a == mod.stable_operational_chunk_id("x.md", 0)
    assert a != mod.stable_operational_chunk_id("x.md", 1)


def test_ingest_operational_dry_run() -> None:
    from src.scripts import ingest_omega_operational_chroma as mod

    rows = mod.load_surface_rows(YAML_PATH)
    code, msgs = mod.ingest_operational_to_chroma(
        root=ROOT,
        rows=rows,
        dry_run=True,
        max_chars=1200,
        overlap=80,
        max_file_chars=500_000,
    )
    assert code == 0
    assert any("dry-run" in m and "core_operational" in m for m in msgs)


def test_ingest_operational_chroma_add() -> None:
    from src.scripts import ingest_omega_operational_chroma as mod

    rows = [
        {
            "repo_path": "README.md",
            "document_role": "operational_surface",
            "anchor_section": "test_focus",
            "title": "",
            "body_sha256": "",
        }
    ]
    col = MagicMock()
    col.get.return_value = {"ids": []}
    fake_emb = [0.051] * 384
    fake_snap = [0.052] * 384
    with (
        patch("src.network.chroma_client.is_configured", return_value=True),
        patch("src.network.chroma_client._get_collection_sync", return_value=col),
        patch("src.network.chroma_client._get_embedding", return_value=fake_emb),
        patch(
            "src.logic_core.crystal_grid_engine.CrystalGridEngine.snap_to_grid",
            return_value=(0, fake_snap),
        ),
    ):
        code, msgs = mod.ingest_operational_to_chroma(
            root=ROOT,
            rows=rows,
            dry_run=False,
            max_chars=500,
            overlap=40,
            max_file_chars=500_000,
        )
    assert code == 0
    col.add.assert_called_once()
    meta0 = col.add.call_args.kwargs["metadatas"][0]
    assert meta0.get("source_collection") == "core_operational"
    assert meta0.get("layer") == "operational_ist"
    assert meta0.get("focus") == "test_focus"
