"""Paar-Benchmark omega_core: mit/ohne Kardan, JSONL + Auswertung (kein Produktivbetrieb)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_writes_valid_pairs(tmp_path: Path) -> None:
    out = tmp_path / "bench.jsonl"
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "src" / "scripts" / "benchmark_whitepaper_anchors.py"),
            "--repeats",
            "2",
            "--out",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "[BENCHMARK_PASS]" in r.stdout

    ev = subprocess.run(
        [
            sys.executable,
            str(ROOT / "src" / "scripts" / "evaluate_whitepaper_benchmark_log.py"),
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert ev.returncode == 0, ev.stderr + ev.stdout

    lines = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 4
    pair_ids = {x["pair_id"] for x in lines}
    assert len(pair_ids) == 2


def test_run_autopoiesis_harness_mit_converges() -> None:
    sys.path.insert(0, str(ROOT))
    import omega_core as oc

    res = oc.run_autopoiesis_harness(enable_kardan=True, p_int_start=1)
    assert res["outcome"] == "converged_complex"
    assert res["iterations"] >= 1
    assert "schleifen_wall_ms" in res
    assert "process_cpu_ms" in res


def test_run_autopoiesis_harness_ohne_paired_matches_iterations() -> None:
    sys.path.insert(0, str(ROOT))
    import omega_core as oc

    mit = oc.run_autopoiesis_harness(enable_kardan=True, p_int_start=1)
    n = mit["iterations"]
    ohne = oc.run_autopoiesis_harness(
        enable_kardan=False,
        p_int_start=1,
        fixed_tick_limit=n,
    )
    assert ohne["outcome"] == "paired_fixed_ticks"
    assert ohne["iterations"] == n
