# -*- coding: utf-8 -*-
"""Phase 2: Kanon → Chroma chunking + Kontrakt (ohne live Chroma)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_chunk_canon_text_empty() -> None:
    from src.scripts import ingest_omega_canon_chroma as mod

    assert mod.chunk_canon_text("", 500, 50) == []
    assert mod.chunk_canon_text("   \n\n  ", 500, 50) == []


def test_chunk_canon_text_splits_paragraphs() -> None:
    from src.scripts import ingest_omega_canon_chroma as mod

    text = "A" * 100 + "\n\n" + "B" * 100 + "\n\n" + "C" * 100
    chunks = mod.chunk_canon_text(text, max_chars=180, overlap=20)
    assert len(chunks) >= 2
    assert all(len(c) <= 200 for c in chunks)


def test_stable_chunk_id_deterministic() -> None:
    from src.scripts import ingest_omega_canon_chroma as mod

    a = mod.stable_chunk_id("docs/x.md", 0)
    b = mod.stable_chunk_id("docs/x.md", 0)
    c = mod.stable_chunk_id("docs/x.md", 1)
    assert a == b
    assert a != c
    assert a.startswith("cc_")


def test_is_text_canon_path() -> None:
    from src.scripts import ingest_omega_canon_chroma as mod

    assert mod._is_text_canon_path("foo.md") is True
    assert mod._is_text_canon_path("x.yml") is True
    assert mod._is_text_canon_path("bin.exe") is False


def test_ingest_dry_run_counts_without_chroma() -> None:
    from src.scripts import ingest_omega_canon_chroma as mod

    rows = [{"repo_path": "README.md", "document_role": "r", "anchor_section": "1", "title": "t"}]
    code, msgs = mod.ingest_canon_to_chroma(
        root=ROOT,
        rows=rows,
        dry_run=True,
        max_chars=800,
        overlap=60,
        max_file_chars=500_000,
    )
    assert code == 0
    assert any("dry-run" in m for m in msgs)
    assert any("Chunk" in m for m in msgs)


def test_ingest_calls_chroma_add_with_snap() -> None:
    from src.scripts import ingest_omega_canon_chroma as mod

    col = MagicMock()
    col.get.return_value = {"ids": []}

    row = {
        "repo_path": "README.md",
        "document_role": "referenced",
        "anchor_section": "1",
        "title": "Readme",
        "body_sha256": "a" * 64,
    }

    fake_emb = [0.051] * 384
    fake_snapped = [0.052] * 384

    with (
        patch(
            "src.network.chroma_client.is_configured",
            return_value=True,
        ),
        patch(
            "src.network.chroma_client._get_collection_sync",
            return_value=col,
        ),
        patch(
            "src.network.chroma_client._get_embedding",
            return_value=fake_emb,
        ),
        patch(
            "src.logic_core.crystal_grid_engine.CrystalGridEngine.snap_to_grid",
            return_value=(0, fake_snapped),
        ),
    ):
        code, msgs = mod.ingest_canon_to_chroma(
            root=ROOT,
            rows=[row],
            dry_run=False,
            max_chars=400,
            overlap=40,
            max_file_chars=500_000,
        )

    assert code == 0
    col.add.assert_called_once()
    call_kw = col.add.call_args.kwargs
    assert "ids" in call_kw and "embeddings" in call_kw
    assert call_kw["embeddings"][0] == fake_snapped
    meta0 = call_kw["metadatas"][0]
    assert meta0.get("type") == "context"
    assert meta0.get("source_collection") == "core_canon"
    assert meta0.get("repo_path") == "README.md"
    assert any("OK" in m for m in msgs)
