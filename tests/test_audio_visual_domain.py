# -*- coding: utf-8 -*-
"""
Veto-Traps: CONCEPT_AUDIO_VISUAL_MASTER V8 (Zwei-Domänen-Theorie).

Beobachtungs-Domäne vs. Resonanz-Domäne; tanh-Projektion ohne Heiler-Weichen.
"""

from __future__ import annotations

import ast
import inspect
import math
from pathlib import Path

import pytest

import src.logic_core.audio_visual_resonance as avr_module
from src.logic_core.audio_visual_resonance import (
    SensorStimulusPipeline,
    accumulate_stimulus_observation,
    build_resonance_embedding_probe,
    coupling_factor,
    focus_intensity_wf,
    interval_spread_observation,
    project_observation_to_resonance,
)
from src.logic_core.crystal_grid_engine import (
    BARYONIC_DELTA as LAMBDA_049,
    CrystalGridEngine,
    EMBEDDING_DIM,
    RESONANCE_LOCK,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "logic_core" / "audio_visual_resonance.py"


def _function_ast(name: str) -> ast.FunctionDef:
    src = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Funktion {name} nicht gefunden")


def test_observation_domain_walls() -> None:
    """Trap 1: 0.0 und große S_raw in der Beobachtungs-Domäne; X_t → 0 bei Stille."""
    assert accumulate_stimulus_observation(0.0, 0.0) == 0.0

    x_large = 0.0
    for _ in range(50):
        x_large = accumulate_stimulus_observation(x_large, 1.0e6)
    assert math.isfinite(x_large)

    x_silence = 100.0
    for _ in range(400):
        x_silence = accumulate_stimulus_observation(x_silence, 0.0)
    assert x_silence == pytest.approx(0.0, abs=1e-9)

    pipe = SensorStimulusPipeline()
    for _ in range(300):
        pipe.tick(0.0)
    assert pipe.x_accumulator == pytest.approx(0.0, abs=1e-12)


def test_resonance_domain_projection() -> None:
    """Trap 2: Grenzen, tanh-only, kein min/max/if-Clamp im Projektionspfad."""
    r0 = project_observation_to_resonance(0.0)
    assert r0 == pytest.approx(LAMBDA_049, rel=0, abs=1e-15)
    assert r0 > 0.0
    assert r0 not in (0.5, 1.0)

    r_inf = project_observation_to_resonance(99_999.0)
    assert r_inf == pytest.approx(RESONANCE_LOCK, rel=0, abs=1e-12)
    assert r_inf < 1.0

    proj_src = inspect.getsource(avr_module.project_observation_to_resonance)
    assert "tanh" in proj_src
    assert "min(" not in proj_src and "max(" not in proj_src
    proj_fn = _function_ast("project_observation_to_resonance")
    for stmt in proj_fn.body:
        assert not isinstance(stmt, ast.If), "Projektion darf keine if-Weiche nutzen"

    acc_fn = _function_ast("accumulate_stimulus_observation")
    for stmt in acc_fn.body:
        assert not isinstance(stmt, ast.If)

    k = coupling_factor(r0)
    assert k == pytest.approx(LAMBDA_049, rel=0, abs=1e-15)
    wf = focus_intensity_wf(k)
    assert math.isfinite(wf) and wf > 0.0

    iv_full = interval_spread_observation(1.0, RESONANCE_LOCK)
    assert iv_full == pytest.approx(1.0, abs=1e-12)


def test_quantization_72_anchor_identity() -> None:
    """Trap 2 Erweiterung: Snap wählt den resonantesten Anker (topologische Nähe)."""
    r_t = project_observation_to_resonance(2.718)
    emb = build_resonance_embedding_probe(r_t)
    assert len(emb) == EMBEDDING_DIM

    aid, snapped = CrystalGridEngine.snap_to_grid(emb)
    CrystalGridEngine._initialize_e6_roots()
    anchors = CrystalGridEngine._anchors
    res_best = CrystalGridEngine.calculate_resonance(emb, snapped)
    wrong_id = (aid + 31) % 72
    res_other = CrystalGridEngine.calculate_resonance(emb, anchors[wrong_id])
    assert res_best > res_other, "Gewählter Anker muss näher sein als ein fernliegender Anker"


def test_continuous_gradient_allocation() -> None:
    """Trap 3: Ableitung von R_t entspricht skaliertem tanh′ (kein Knick)."""
    span = RESONANCE_LOCK - LAMBDA_049

    def dr_dx(x: float) -> float:
        t = math.tanh(x)
        return span * (1.0 - t * t)

    for x in [0.0, 0.049, 1.0, 3.14159, 12.0]:
        h = 1e-8
        fd = (project_observation_to_resonance(x + h) - project_observation_to_resonance(x - h)) / (
            2.0 * h
        )
        assert fd == pytest.approx(dr_dx(x), rel=1e-5, abs=1e-7)

    xs = [i * 0.1 for i in range(-5, 80)]
    prev_r = project_observation_to_resonance(xs[0])
    for x in xs[1:]:
        r = project_observation_to_resonance(x)
        assert r >= prev_r - 1e-15, "R_t muss monoton in X_t wachsen (tanh)"
        prev_r = r
