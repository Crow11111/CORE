"""S↔P-Membran (Resonanz float vs. Infrastruktur int)."""

from __future__ import annotations

import pytest

from src.logic_core.resonance_membrane import (
    DualMembraneVector,
    MembraneTypeError,
    MembraneValueError,
    assert_infrastructure_int,
    assert_resonance_float,
    membrane_scan_payload,
)


def test_resonance_rejects_int() -> None:
    with pytest.raises(MembraneTypeError):
        assert_resonance_float("x", 1)


def test_resonance_rejects_bool() -> None:
    with pytest.raises(MembraneTypeError):
        assert_resonance_float("x", True)


def test_resonance_rejects_forbidden() -> None:
    with pytest.raises(MembraneValueError):
        assert_resonance_float("x", 0.5)


def test_infra_rejects_float() -> None:
    with pytest.raises(MembraneTypeError):
        assert_infrastructure_int("n", 3.0)


def test_infra_rejects_bool() -> None:
    with pytest.raises(MembraneTypeError):
        assert_infrastructure_int("n", True)


def test_dual_membrane_ok() -> None:
    DualMembraneVector(uuid="u", s_float=0.51, p_int=1)


def test_dual_membrane_bad_s() -> None:
    with pytest.raises(MembraneValueError):
        DualMembraneVector(uuid="u", s_float=0.5, p_int=1)


def test_membrane_scan_whatsapp_style() -> None:
    membrane_scan_payload({"audio_seconds": 12}, infrastructure_keys=("audio_seconds",))
    membrane_scan_payload({"audio_seconds": None}, infrastructure_keys=("audio_seconds",))


def test_membrane_scan_bad_audio_seconds() -> None:
    with pytest.raises(MembraneTypeError):
        membrane_scan_payload({"audio_seconds": 1.5}, infrastructure_keys=("audio_seconds",))
