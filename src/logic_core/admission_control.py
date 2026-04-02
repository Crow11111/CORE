class StateTransitionError(Exception):
    """Exception raised for invalid state transitions in OmegaJob."""
    pass

def calculate_system_drift(R: float, I: float) -> float:
    """
    Calculates the system drift D based on Resources (R) and Information Gain (I).
    Formula: D = clamp(0.049, R / (I + 1e-9), 0.951)
    Enforces symmetry break if the result falls in [0.499, 0.501] -> 0.51.
    """
    raw_d = R / (I + 1e-9)
    
    # Clamp to [0.049, 0.951]
    d = max(0.049, min(raw_d, 0.951))
    
    # Symmetry break: Anti-0.5
    if 0.499 <= d <= 0.501:
        return 0.51
        
    return d

def admission_check(drift: float) -> bool:
    """
    Circuit Breaker: Decides whether to accept the request based on drift.
    Accepts if drift < 0.90, rejects otherwise.
    """
    return drift < 0.90

class OmegaJob:
    """
    Global Workspace State Machine model for a job.
    """
    VALID_TRANSITIONS = {
        "received": ["queued", "failed"],
        "queued": ["processing", "failed"],
        "processing": ["blocked_on_evidence", "efference_submitted", "failed"],
        "blocked_on_evidence": ["processing", "failed"],
        "efference_submitted": ["vetoed", "released", "failed"],
        "vetoed": ["failed"],
        "released": ["sent", "failed"],
        "sent": ["receipt_matched", "failed"],
        "receipt_matched": [],
        "failed": []
    }

    def __init__(self):
        self.state = "received"

    def transition_to(self, new_state: str) -> None:
        """
        Transitions the job to a new state if causality is respected.
        """
        if new_state not in self.VALID_TRANSITIONS.get(self.state, []):
            raise StateTransitionError(f"Invalid transition from {self.state} to {new_state}")
        
        self.state = new_state
