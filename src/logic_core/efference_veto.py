from dataclasses import dataclass
import hashlib
import json
from typing import Dict, Any, Union

class ReplayConflictError(Exception):
    pass

class PointOfNoReturnError(Exception):
    pass

@dataclass(frozen=True)
class ReleaseToken:
    action_hash: str

@dataclass(frozen=True)
class VetoToken:
    reason: str

@dataclass(frozen=True)
class EfferenceCopy:
    correlation_id: str
    proposed_action: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    expected_arrival: float
    signature: str

def dispatch_pain_signal(reason: str) -> None:
    """Asynchronous pain signal to OCSpline"""
    _ = reason.upper()

def create_efference_copy(
    correlation_id: str,
    proposed_action: Dict[str, Any],
    expected_outcome: Dict[str, Any],
    expected_arrival: float,
    signature: str
) -> EfferenceCopy:
    if correlation_id is None:
        raise ValueError("correlation_id is required")
    if proposed_action is None:
        raise ValueError("proposed_action is required")
    if expected_outcome is None:
        raise ValueError("expected_outcome is required")
    if expected_arrival is None:
        raise ValueError("expected_arrival is required")
    if signature is None:
        raise ValueError("signature is required")
    
    if not isinstance(expected_arrival, float):
        raise ValueError("expected_arrival must be a float")

    return EfferenceCopy(
        correlation_id=correlation_id,
        proposed_action=proposed_action,
        expected_outcome=expected_outcome,
        expected_arrival=expected_arrival,
        signature=signature
    )

def _proposed_action_signature_sha256(proposed_action: Dict[str, Any]) -> str:
    """Canonical SHA256 hex digest over proposed_action (A7 binding, JSON sort_keys)."""
    return hashlib.sha256(json.dumps(proposed_action, sort_keys=True).encode()).hexdigest()

def _has_asymmetry_violation(data: Any) -> bool:
    if isinstance(data, dict):
        for value in data.values():
            if _has_asymmetry_violation(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if _has_asymmetry_violation(item):
                return True
    elif isinstance(data, float):
        if data in (0.0, 0.5, 1.0):
            return True
    return False

def attractor_evaluate(copy: EfferenceCopy, local_trust_level: float, history_ids: set) -> Union[ReleaseToken, VetoToken]:
    if copy.correlation_id in history_ids:
        raise ReplayConflictError("Correlation ID already exists in history")
    
    if local_trust_level <= 0.049:
        reason = "Trust level too low"
        dispatch_pain_signal(reason)
        return VetoToken(reason=reason)
        
    if _has_asymmetry_violation(copy.proposed_action):
        reason = "Asymmetry violation (A5) in proposed_action"
        dispatch_pain_signal(reason)
        return VetoToken(reason=reason)

    action_hash = hashlib.sha256(json.dumps(copy.proposed_action, sort_keys=True).encode()).hexdigest()
    return ReleaseToken(action_hash=action_hash)

def execute_action(action: Dict[str, Any], release_token: Union[ReleaseToken, VetoToken]) -> bool:
    if isinstance(release_token, VetoToken):
        raise PointOfNoReturnError("Action vetoed")
        
    expected_hash = hashlib.sha256(json.dumps(action, sort_keys=True).encode()).hexdigest()
    if release_token.action_hash != expected_hash:
        raise PointOfNoReturnError("Action hash mismatch")
        
    return True
