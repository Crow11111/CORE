import pytest
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock
import hashlib
import json

from src.logic_core.efference_veto import (
    create_efference_copy,
    attractor_evaluate,
    execute_action,
    ReleaseToken,
    VetoToken,
    ReplayConflictError,
    PointOfNoReturnError,
    EfferenceCopy,
    dispatch_pain_signal,
)


def _canonical_action_signature(action: dict) -> str:
    return hashlib.sha256(json.dumps(action, sort_keys=True).encode()).hexdigest()

def test_efference_copy_missing_fields():
    # Trap 1A: Das Fehlen eines Feldes führt zu einem harten ValueError
    with pytest.raises(ValueError):
        create_efference_copy(
            correlation_id="123",
            proposed_action={"action": "move"},
            expected_outcome=None,  # Missing
            expected_arrival=1.5,
            signature="valid_sig"
        )

def test_efference_copy_immutability():
    # Trap 1B: Veränderung führt zu FrozenInstanceError
    copy = create_efference_copy(
        correlation_id="123",
        proposed_action={"action": "move"},
        expected_outcome={"result": "success"},
        expected_arrival=1.5,
        signature="valid_sig"
    )
    with pytest.raises(FrozenInstanceError):
        copy.expected_arrival = 9.9

def test_attractor_release():
    # Trap 2A: Valid trust, new ID, matching A7 signature -> ReleaseToken
    proposed = {"action": "move"}
    copy = create_efference_copy(
        correlation_id="123",
        proposed_action=proposed,
        expected_outcome={"result": "success"},
        expected_arrival=1.5,
        signature=_canonical_action_signature(proposed),
    )
    history_ids = set()
    token = attractor_evaluate(copy, local_trust_level=0.05, history_ids=history_ids)
    
    assert isinstance(token, ReleaseToken)
    assert token.action_hash == _canonical_action_signature(proposed)

def test_attractor_veto_trust(monkeypatch):
    # Trap 2B: Trust <= 0.049 -> VetoToken
    copy = create_efference_copy(
        correlation_id="124",
        proposed_action={"action": "move"},
        expected_outcome={"result": "success"},
        expected_arrival=1.5,
        signature="valid_sig"
    )
    history_ids = set()
    
    spy = MagicMock()
    monkeypatch.setattr("src.logic_core.efference_veto.dispatch_pain_signal", spy)
    
    token = attractor_evaluate(copy, local_trust_level=0.049, history_ids=history_ids)
    
    assert isinstance(token, VetoToken)
    spy.assert_called_once()

def test_attractor_veto_tampered_signature(monkeypatch):
    # Trap 2E: Manipulierte Signatur trotz Trust > 0.049 -> VetoToken (A7 / Trust collapse)
    proposed = {"action": "move", "target": "node-7"}
    good_sig = _canonical_action_signature(proposed)
    tampered = good_sig[:-1] + ("0" if good_sig[-1] != "0" else "1")
    copy = create_efference_copy(
        correlation_id="127",
        proposed_action=proposed,
        expected_outcome={"result": "success"},
        expected_arrival=1.5,
        signature=tampered,
    )
    spy = MagicMock()
    monkeypatch.setattr("src.logic_core.efference_veto.dispatch_pain_signal", spy)
    token = attractor_evaluate(copy, local_trust_level=0.05, history_ids=set())
    assert isinstance(token, VetoToken)
    assert "signature mismatch" in token.reason
    spy.assert_called_once()


def test_attractor_veto_asymmetry(monkeypatch):
    # Trap 2C: Asymmetry violation -> VetoToken
    copy = create_efference_copy(
        correlation_id="125",
        proposed_action={"action": "move", "speed": 0.5},
        expected_outcome={"result": "success"},
        expected_arrival=1.5,
        signature="valid_sig"
    )
    history_ids = set()
    
    spy = MagicMock()
    monkeypatch.setattr("src.logic_core.efference_veto.dispatch_pain_signal", spy)
    
    token = attractor_evaluate(copy, local_trust_level=0.5, history_ids=history_ids)
    
    assert isinstance(token, VetoToken)
    spy.assert_called_once()

def test_attractor_replay():
    # Trap 2D: correlation_id in history_ids -> ReplayConflictError
    copy = create_efference_copy(
        correlation_id="126",
        proposed_action={"action": "move"},
        expected_outcome={"result": "success"},
        expected_arrival=1.5,
        signature="valid_sig"
    )
    history_ids = {"126"}
    with pytest.raises(ReplayConflictError):
        attractor_evaluate(copy, local_trust_level=0.5, history_ids=history_ids)

def test_execute_action_allowed():
    # Trap 3A: Valid ReleaseToken, hash matches -> True
    action = {"action": "move"}
    expected_hash = hashlib.sha256(json.dumps(action, sort_keys=True).encode()).hexdigest()
    token = ReleaseToken(action_hash=expected_hash)
    
    result = execute_action(action, token)
    assert result is True

def test_execute_action_denied_veto():
    # Trap 3B: VetoToken -> PointOfNoReturnError
    action = {"action": "move"}
    token = VetoToken(reason="Trust collapse")
    
    with pytest.raises(PointOfNoReturnError):
        execute_action(action, token)

def test_execute_action_denied_tampering():
    # Trap 3B: Hash mismatch -> PointOfNoReturnError
    action = {"action": "move"}
    token = ReleaseToken(action_hash="wrong_hash")
    
    with pytest.raises(PointOfNoReturnError):
        execute_action(action, token)
