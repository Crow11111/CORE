import pytest
from src.logic_core.admission_control import (
    calculate_system_drift,
    admission_check,
    OmegaJob,
    StateTransitionError
)

def test_trap1_drift_calculator_basic():
    """Test A: Basis - R=0.2, I=0.8 -> D muss korrekt berechnet werden."""
    # R / (I + 1e-9) -> 0.2 / 0.8 = 0.25
    result = calculate_system_drift(0.2, 0.8)
    assert isinstance(result, float)
    assert abs(result - 0.25) < 1e-6

def test_trap1_drift_calculator_upper_limit():
    """Test B: A5-Schutz Oben - R=1.0, I=0.0 -> Darf nicht crashen, muss bei 0.951 kappen."""
    result = calculate_system_drift(1.0, 0.0)
    assert isinstance(result, float)
    assert result == 0.951

def test_trap1_drift_calculator_lower_limit():
    """Test C: A5-Schutz Unten - R=0.0, I=0.951 -> Muss bei 0.049 kappen."""
    result = calculate_system_drift(0.0, 0.951)
    assert isinstance(result, float)
    assert result == 0.049

def test_trap1_drift_calculator_symmetry_break():
    """Test D: Symmetriebruch / Anti-0.5 - Ergibt die Rechnung 0.5 (Band 0.499-0.501), MUSS auf 0.51 snappen."""
    # R=0.5, I=1.0 -> R/(I+1e-9) = ~0.5
    result = calculate_system_drift(0.5, 1.0)
    assert isinstance(result, float)
    assert result == 0.51
    
    # 0.499 -> wir geben etwas Puffer für floating point ungenauigkeit
    result_low = calculate_system_drift(0.499000002, 1.0)
    assert result_low == 0.51
    
    # 0.501
    result_high = calculate_system_drift(0.500999999, 1.0)
    assert result_high == 0.51

def test_trap2_circuit_breaker_accept():
    """Test A: Wenn drift < 0.90 -> Return True (Annahme)."""
    assert admission_check(0.89) is True
    assert admission_check(0.049) is True

def test_trap2_circuit_breaker_reject():
    """Test B: Wenn drift >= 0.90 -> Return False (Abweisung)."""
    assert admission_check(0.90) is False
    assert admission_check(0.951) is False

def test_trap3_state_machine_valid_transition():
    """Test A (Erlaubter Sprung): Wechsel von queued zu processing muss erfolgreich sein."""
    job = OmegaJob()
    job.transition_to("queued")
    job.transition_to("processing")
    assert job.state == "processing"

def test_trap3_state_machine_invalid_transition():
    """Test B (Verbotener Kausal-Sprung): Wechsel von received direkt zu sent MUSS StateTransitionError werfen."""
    job = OmegaJob()
    with pytest.raises(StateTransitionError):
        job.transition_to("sent")
