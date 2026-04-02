# -*- coding: utf-8 -*-
r"""
OMEGA WICK ROTATION MODULE
--------------------------
Stellt Funktionen zur Transformation zwischen reeller Minkowski-Zeit
und imaginärer euklidischer Zeit bereit.

Logik: t -> \tau = i * t
"""

import numpy as np
import logging
from typing import Union, List, Tuple
from src.logic_core.projection_layer import projection_horizon

logger = logging.getLogger("OMEGA_WICK")

def enter_imaginary_time(embedding: Union[List[float], np.ndarray], current_time_t: float = 1.0) -> Tuple[np.ndarray, complex]:
    """
    Transformiert den Zustand in die imaginäre Zeit.
    \tau = i * t
    """
    vec = np.array(embedding, dtype=np.float64)
    # Wick-Rotation via Projection Layer
    euclidean_state = projection_horizon.enter_imaginary_time(vec)
    tau = current_time_t * 1j

    return euclidean_state, tau

def inverse_wick_rotation(imaginary_state: np.ndarray, asymmetry_gradient: float = 0.049) -> np.ndarray:
    """
    Rückkehr in die kausale Realität (Minkowski-Raum).
    Nutzt den Asymmetrie-Gradienten zur Symmetriebrechung.
    """
    # Kollaps via Projection Layer (L2-Norm)
    minkowski_state = projection_horizon.exit_imaginary_time(imaginary_state)

    # Symmetriebrechung einrechnen
    minkowski_state = minkowski_state * (1.0 + asymmetry_gradient)

    # Axiom A5 Check via Projection Layer (wird dort bereits gehandhabt,
    # aber wir stellen sicher, dass keine 1.0 durch den Gradienten entsteht)
    minkowski_state = np.where(minkowski_state >= 1.0, 0.951, minkowski_state)

    return minkowski_state
