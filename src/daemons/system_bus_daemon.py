# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import time
import hashlib
import json
from typing import Dict, Any, Optional
from loguru import logger

from src.config.core_state import BASE_STATE, BARYONIC_DELTA, StateVector
from src.logic_core.crystal_grid_engine import CrystalGridEngine, validate_state_vector

class SystemBus:
    """
    Der SystemBusDaemon (Ring 0).
    Hält den Global Resonance Vector (GRV) im RAM und verwaltet den Causal Hash.
    """

    def __init__(self):
        # Initialzustand basierend auf BASE_STATE
        self._grv: Dict[str, float] = {
            "x_car_cdr": BASE_STATE.x_car_cdr,
            "y_gravitation": BASE_STATE.y_gravitation,
            "z_widerstand": BASE_STATE.z_widerstand,
            "w_takt": BASE_STATE.w_takt,
            "vps_networking": 0.49,  # Initialer Symmetriebruch
            "volume_persistence": 0.51
        }
        
        # Causal Hash Initialisierung (Genesis Hash)
        self._state_hash = hashlib.sha256(b"CORE_GENESIS_2026").hexdigest()
        self._last_tick = time.time()
        
        logger.info("[BUS] SystemBus initialisiert. Genesis Hash: {}", self._state_hash)

    def get_grv(self) -> Dict[str, float]:
        """Gibt den aktuellen Global Resonance Vector zurück."""
        return dict(self._grv)

    def get_state_hash(self) -> str:
        """Gibt den aktuellen Causal Hash zurück."""
        return self._state_hash

    def entropy_tick(self):
        """
        Berechnet den entropischen Zerfall (Time Decay).
        Alle Floats im GRV werden um 1% reduziert.
        """
        now = time.time()
        elapsed = now - self._last_tick
        
        # Wir skalieren den Zerfall nicht linear zur Zeit, 
        # sondern pro Takt (Aufruf). 1% Reduktion.
        for key in self._grv:
            # Reduktion um 1%
            new_val = self._grv[key] * 0.99
            
            # Baryonisches Limit beachten (Axiom A5/A6 via CrystalGridEngine)
            snapped = CrystalGridEngine.apply_operator_query(new_val)
            self._grv[key] = float(abs(snapped))
            
        self._last_tick = now
        self._update_hash()
        logger.debug("[BUS] Entropy Tick ausgeführt. GRV kühlt ab.")

    def apply_delta(self, json_delta: Dict[str, Any]) -> str:
        """
        Integriert ein Delta in den GRV und aktualisiert den Causal Hash.
        
        Args:
            json_delta: Schema gemäß docs/01_CORE_DNA/CAUSAL_HASH_PROTOCOL.md
        """
        causal_receipt = json_delta.get("causal_receipt", {})
        base_hash_t = causal_receipt.get("base_hash_t")
        latency_ms = causal_receipt.get("compute_latency_ms", 0)

        # 1. Strict Concurrency Check
        if base_hash_t and base_hash_t != self._state_hash:
            logger.warning("[BUS] Hash Divergenz erkannt! Agent Base: {} | Bus: {}", base_hash_t, self._state_hash)
            # In Phase 1 erlauben wir den Merge, loggen aber die Divergenz.

        # 2. Time Decay basierend auf Latenz (Phase-Amplitude Coupling)
        # Wenn der Agent 1.5s gebraucht hat, simulieren wir den Zerfall in dieser Zeit.
        decay_factor = 0.99 ** (max(1, latency_ms // 100)) # 1% pro 100ms
        for key in self._grv:
            self._grv[key] *= decay_factor

        # 3. Integration Dimensional Shift
        dim_shift = json_delta.get("dimensional_shift", {})
        self._grv["x_car_cdr"] += dim_shift.get("x_car_cdr_delta", 0.0)
        self._grv["y_gravitation"] += dim_shift.get("y_gravitation_delta", 0.0)
        self._grv["z_widerstand"] += dim_shift.get("z_resistance_delta", 0.0)

        # 4. Integration Semantic Nodes
        semantic_nodes = json_delta.get("semantic_nodes_hot", {})
        for node, val in semantic_nodes.items():
            current = self._grv.get(node, BARYONIC_DELTA)
            self._grv[node] = current + val

        # 5. Axiom Enforcement & Snapping
        for key in list(self._grv.keys()):
            val = self._grv[key]
            # Sicherstellen, dass keine verbotenen Werte entstehen
            snapped = CrystalGridEngine.apply_operator_query(val)
            self._grv[key] = float(abs(snapped))
            
            # Garbage Collection: Baryonisches Delta
            if self._grv[key] < BARYONIC_DELTA:
                if key not in ["x_car_cdr", "y_gravitation", "z_widerstand", "w_takt"]:
                    logger.debug("[BUS] Node {} unter Baryonischem Limit -> Purge.", key)
                    del self._grv[key]
                else:
                    self._grv[key] = BARYONIC_DELTA

        # 6. Update Causal Hash
        new_hash = self._update_hash()
        logger.info("[BUS] Delta integriert. Neuer State Hash: {}", new_hash)
        return new_hash

    def _update_hash(self) -> str:
        """Berechnet den neuen State_Hash(t)."""
        data = {
            "prev_hash": self._state_hash,
            "grv": self._grv,
            "ts": time.time()
        }
        hash_input = json.dumps(data, sort_keys=True).encode()
        self._state_hash = hashlib.sha256(hash_input).hexdigest()
        return self._state_hash

# Singleton Instanz für den Daemon-Prozess
bus_instance = SystemBus()
