# -*- coding: utf-8 -*-
"""Kontrakt: docker ps (tab) vs. Host-Ports — ohne SSH (Zero-Trust Unit)."""
from __future__ import annotations

from src.scripts.verify_vps_docker_port_contract import verify_docker_ps_lines_tabbed


def test_chroma_maps_contract_port() -> None:
    lines = [
        "chroma-uvmy-chromadb-1\tUp 2 hours\t0.0.0.0:32779->8000/tcp",
    ]
    ok, msgs = verify_docker_ps_lines_tabbed(lines)
    assert ok, msgs
    assert any("32779" in m and "[OK]" in m for m in msgs)


def test_chroma_wrong_host_port_fails() -> None:
    lines = [
        "chroma-uvmy-chromadb-1\tUp 2 hours\t0.0.0.0:32768->8000/tcp",
    ]
    ok, msgs = verify_docker_ps_lines_tabbed(lines)
    assert not ok
    assert any("[FAIL]" in m for m in msgs)


def test_kong_three_ports_required() -> None:
    lines = [
        "kong-s7rk-kong-1\tUp 2 hours\t"
        "0.0.0.0:32776->8000/tcp, 0.0.0.0:32777->8001/tcp, 0.0.0.0:32778->8002/tcp",
    ]
    ok, msgs = verify_docker_ps_lines_tabbed(lines)
    assert ok, msgs


def test_evolution_postgres_not_matched_for_api_port() -> None:
    lines = [
        "evolution-api-yxa5-postgres-1\tUp 2 hours\t5432/tcp",
    ]
    ok, msgs = verify_docker_ps_lines_tabbed(lines)
    assert ok, msgs
    assert not any("evolution-api" in m and "[FAIL]" in m for m in msgs)
