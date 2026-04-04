import pytest
from src.logic_core.efference_veto import ReleaseToken, VetoToken
from src.logic_core.temporal_alignment import (
    calculate_prediction_error,
    adjust_trust_level,
    apply_kardanic_rescue,
    dispatch_to_evolution,
    HawkingRadiationDropError,
)

def test_trap_1_semantic_match():
    # Test A: LTP, expected and receipt match, no timeout -> PE = 0.049
    expected = {"state": "active", "value": 42}
    receipt = {"state": "active", "value": 42}
    pe = calculate_prediction_error(expected, receipt, is_timeout=False)
    assert pe == 0.049
    assert isinstance(pe, float)

def test_trap_1_semantic_mismatch():
    # Test B: Mismatch, PE clamped to avoid 0.5, 1.0, 0.0. Max PE is 0.951.
    expected = {"state": "active", "value": 42}
    receipt = {"state": "inactive", "value": 0}
    pe = calculate_prediction_error(expected, receipt, is_timeout=False)
    assert isinstance(pe, float)
    assert pe != 0.0
    assert pe != 0.5
    assert pe != 1.0
    assert pe <= 0.951
    assert pe >= 0.049

def test_trap_1_timeout():
    # Test C: Timeout -> PE = 0.951
    expected = {"state": "active", "value": 42}
    receipt = {}
    pe = calculate_prediction_error(expected, receipt, is_timeout=True)
    assert pe == 0.951
    assert isinstance(pe, float)

def test_trap_2_trust_recovery():
    # Test A: Erholung, PE < 0.5 -> logarithmic rise (geclampt auf max 0.951, keine 0.5/1.0)
    current_trust = 0.1
    pe = 0.2
    new_trust = adjust_trust_level(current_trust, pe)
    assert isinstance(new_trust, float)
    assert new_trust > current_trust
    assert new_trust <= 0.951
    assert new_trust != 0.5

def test_trap_2_trust_collapse():
    # Test B: Single-Trial Aversive Learning, PE >= 0.5 -> crash to 0.049
    current_trust = 0.8
    pe = 0.6
    new_trust = adjust_trust_level(current_trust, pe)
    assert new_trust == 0.049
    assert isinstance(new_trust, float)

def test_trap_3_no_rescue():
    # Test A: Kein Eingriff, wenn trust_level > 0.049
    with pytest.raises(RuntimeError):
        apply_kardanic_rescue(context_mass=50.0, trust_level=0.1, pe=0.2)

def test_trap_3_kardanic_rescue():
    # Test B: Drehimpulsumkehr & Phasensprung + P-Vektor (Isolation-Queue) inkrementiert pro Rescue
    context_mass = 50.0
    trust_level = 0.049
    pe = 0.8
    rescue_vector_1, p1 = apply_kardanic_rescue(context_mass, trust_level, pe)
    rescue_vector_2, p2 = apply_kardanic_rescue(context_mass, trust_level, pe)
    assert isinstance(rescue_vector_1, complex)
    assert isinstance(p1, int)
    assert rescue_vector_1 == (-context_mass) * 1j
    assert rescue_vector_2 == rescue_vector_1
    assert p2 == p1 + 1

def test_trap_3_hawking_radiation():
    # Test C: Zu steiler Absturz
    with pytest.raises(HawkingRadiationDropError):
        apply_kardanic_rescue(context_mass=1500.0, trust_level=0.049, pe=0.951)

def test_trap_4_dispatch_success():
    # Test A: Exakt ReleaseToken (A7 Typ-Kontrakt) -> state "sent"
    payload = {"data": "test"}
    token = ReleaseToken(action_hash="deadbeef")
    result = dispatch_to_evolution(payload, token)
    assert result == "sent"
    assert payload.get("state") == "sent"

def test_trap_4_dispatch_failure():
    # Test B: None oder Nicht-ReleaseToken -> ValueError
    payload = {"data": "test"}
    with pytest.raises(ValueError):
        dispatch_to_evolution(payload, None)
    with pytest.raises(ValueError):
        dispatch_to_evolution(payload, object())
    with pytest.raises(ValueError):
        dispatch_to_evolution(payload, VetoToken(reason="vetoed"))
