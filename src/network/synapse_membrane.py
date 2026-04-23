import time
from typing import Dict, Any

class OpenClawSynapse:
    """
    Biologisch inspirierter Ionenkanal (Synapse) für OpenClaw-Worker.
    Verhindert Agenten-Amokläufe und schützt den SystemBus (GRV) vor Reizüberflutung.
    """

    def __init__(self) -> None:
        self._state: Dict[str, Dict[str, float]] = {}
        self._base_refractory_ms: float = 2049.0
        self._phi: float = 1.6180339

    def _get_time_ms(self) -> float:
        return time.time() * 1000.0

    def is_refractory(self, worker_id: str) -> bool:
        """Prüft, ob sich die Synapse für den gegebenen Worker in der Refraktärzeit befindet."""
        now_ms = self._get_time_ms()
        worker_state = self._state.get(worker_id)
        if worker_state is None:
            return False
        
        locked_until = worker_state.get("locked_until", 0.0)
        return now_ms < locked_until

    def trigger_action_potential(self, worker_id: str, causal_delta: Dict[str, Any]) -> Dict[str, float]:
        """
        Löst das Aktionspotenzial aus und verriegelt die Synapse.
        Die lock_duration berechnet sich dynamisch anhand der z_resistance_delta.
        """
        now_ms = self._get_time_ms()
        
        z_resistance_delta = 0.0
        dim_shift = causal_delta.get("dimensional_shift")
        if isinstance(dim_shift, dict):
            z_resistance_delta = float(dim_shift.get("z_resistance_delta", 0.0))
        else:
            z_resistance_delta = float(causal_delta.get("z_resistance_delta", 0.0))

        # O2-Korrektur (Axiom A5): Asymmetrische Skalierung mit PHI
        # Formel: lock_duration = base_refractory_ms * (0.951 + (z_resistance_delta * 1.6180339))
        lock_duration = self._base_refractory_ms * (0.951 + (z_resistance_delta * self._phi))
        
        # Absolute Baseline von 549.0 ms darf nicht unterschritten werden
        if lock_duration < 549.0:
            lock_duration = 549.0

        locked_until = now_ms + lock_duration

        self._state[worker_id] = {
            "last_fired": now_ms,
            "locked_until": locked_until
        }

        # Anti-Heroin-Validator verlangt Healer-Aktion
        print(f"[SYNAPSE] Action Potential für {worker_id}: locked for {lock_duration:.2f}ms")

        return {
            "locked_until": locked_until,
            "lock_duration_ms": lock_duration
        }

synapse_instance = OpenClawSynapse()
