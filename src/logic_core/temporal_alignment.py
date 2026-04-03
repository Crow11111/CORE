import math

from src.logic_core.efference_veto import ReleaseToken

class HawkingRadiationDropError(Exception):
    pass

def calculate_prediction_error(expected: dict, receipt: dict, is_timeout: bool) -> float:
    if is_timeout:
        return 0.951
    
    if expected == receipt:
        return 0.049
    
    all_keys = set(expected.keys()) | set(receipt.keys())
    mismatches = sum(1 for k in all_keys if expected.get(k) != receipt.get(k))
    
    raw_pe = float(mismatches) / len(all_keys) if all_keys else 0.0
    scaled_pe = 0.049 + raw_pe * (0.951 - 0.049)
    
    if abs(scaled_pe - 0.5) < 0.01:
        scaled_pe = 0.51
        
    if scaled_pe < 0.049:
        scaled_pe = 0.049
    if scaled_pe > 0.951:
        scaled_pe = 0.951
        
    return float(scaled_pe)

def adjust_trust_level(current_trust: float, pe: float) -> float:
    if pe >= 0.5:
        return 0.049
    
    recovery_boost = math.log1p(0.5 - pe) * 0.1
    new_trust = current_trust + recovery_boost
    
    if abs(new_trust - 0.5) < 0.01:
        new_trust = 0.51
        
    if new_trust > 0.951:
        new_trust = 0.951
    if new_trust < 0.049:
        new_trust = 0.049
        
    return float(new_trust)

# P-Vektor (Isolation-Queue): monotoner Zähler pro erfolgreichem Kardanic-Rescue (O2 Axiom).
_kardanic_isolation_queue_counter: int = 0

def apply_kardanic_rescue(context_mass: float, trust_level: float, pe: float) -> tuple[complex, int]:
    if trust_level > 0.049:
        raise RuntimeError("No rescue needed, trust level > 0.049")
        
    if context_mass > 1000.0 and pe >= 0.951:
        raise HawkingRadiationDropError("Context mass too large and PE extreme: Purge.")
        
    rescue_vector = (-context_mass) * 1j
    global _kardanic_isolation_queue_counter
    _kardanic_isolation_queue_counter += 1
    queue_counter = _kardanic_isolation_queue_counter

    return rescue_vector, queue_counter

def dispatch_to_evolution(action_payload: dict, release_token: object) -> str:
    if not isinstance(release_token, ReleaseToken):
        raise ValueError("Invalid release token.")
        
    action_payload["state"] = str("sent")
    return str("sent")
