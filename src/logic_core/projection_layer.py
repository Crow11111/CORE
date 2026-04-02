# -*- coding: utf-8 -*-
r"""
OMEGA PROJECTION LAYER (THE ARTIFICIAL HORIZON)
----------------------------------------------
Zentrale Instanz zur Transformation zwischen hochdimensionalen 6D-Zuständen (E6-Gitter, Torus-Topologie)
und niederdimensionalen 3D/1D-Schnittstellen (ChromaDB, UI, Hardware).

Implementiert TOSS (Torus-to-Stratified-Sphere) und Wick-Rotation (\tau = i*t).
"""

import numpy as np
import logging
from typing import Union, List, Tuple

logger = logging.getLogger("OMEGA_PROJECTION")

class ProjectionLayer:
    def __init__(self, baryonic_delta: float = 0.049):
        self.LAMBDA = baryonic_delta
        self.E6_DIM = 78  # Dimension der Lie-Gruppe E6
        self.TORUS_DIM = 6
        logger.info(f"[PROJECTION] Initialisiert mit Delta={self.LAMBDA}")

    def toss_projection(self, torus_vector: Union[List[float], np.ndarray]) -> List[float]:
        """
        Torus-to-Stratified-Sphere (TOSS) Transformation.
        Mappt periodische Winkelkoordinaten auf dem Torus in einen euklidischen Raum,
        indem jede Koordinate auf den Einheitskreis gehoben wird (cos(x), sin(x)).
        Verdoppelt die Dimension (N -> 2N).
        Verhindert den L2-Norm-Kollaps in ChromaDB.
        """
        v = np.array(torus_vector, dtype=np.float64)
        # Wir heben den Vektor auf den Einheitskreis
        # Axiom A5: Keine 1.0. Wir skalieren leicht mit (1-Delta)
        scale = 1.0 - self.LAMBDA
        
        # Vectorized cos and sin for speed
        c = np.cos(v) * scale
        s = np.sin(v) * scale
        
        # Interleave cos and sin: [cos1, sin1, cos2, sin2, ...]
        projection = np.empty(2 * v.size, dtype=np.float64)
        projection[0::2] = c
        projection[1::2] = s
        
        return projection.tolist()

    def enter_imaginary_time(self, state_vector: np.ndarray) -> np.ndarray:
        """
        Wick-Rotation: t -> \tau = i * t.
        Transformiert die Minkowski-Metrik in eine positiv-definite euklidische Metrik.
        Erlaubt die Berechnung von Ground-States ohne kausale Deadlocks.
        """
        logger.info("[PROJECTION] Wick-Rotation: Eintritt in die imaginäre Zeit (Euclidean Mode)")
        # In Python entspricht die Multiplikation mit 1j der Wick-Rotation
        return state_vector * 1j

    def exit_imaginary_time(self, imaginary_state: np.ndarray) -> np.ndarray:
        """
        Inverse Wick-Rotation: \tau -> t.
        Kollabiert den euklidischen Zustand zurück in die Minkowski-Raumzeit der Hardware.
        Nutzt die L2-Norm (abs()) zur Dimensionsreduktion (Kollaps in die Zeit).
        """
        logger.info("[PROJECTION] Inverse Wick-Rotation: Kollaps in die Kausalität (Minkowski Mode)")
        # Der Betrag (abs) ist der physikalische Kollaps auf den reellen Strahl
        collapsed = np.abs(imaginary_state)
        
        # Axiom A5 Check: Snapping bei Symmetrie-Gefangenschaft
        collapsed = np.where(collapsed >= 1.0, 0.951, collapsed)
        collapsed = np.where(collapsed <= 0.0, 0.049, collapsed)
        
        return collapsed

    def calculate_natural_transformation(self, funktor_F: np.ndarray, funktor_G: np.ndarray) -> np.ndarray:
        """
        Berechnet den Morphismus (die natürliche Transformation) zwischen zwei Funktoren.
        Ersatz für Git-Sync/Diff. Definiert den kontinuierlichen Zustands-Morphismus.
        """
        # In der Vektor-Kategorie ist die Transformation der Differenz-Vektor (Verschiebung)
        alpha = funktor_G - funktor_F
        # Wir normieren die Transformation auf das Baryonische Delta
        norm = np.linalg.norm(alpha)
        if norm > self.LAMBDA:
             alpha = (alpha / norm) * self.LAMBDA
        
        return alpha

    def get_artificial_horizon(self, state_vector: List[float]) -> dict:
        """
        Projiziert den 6D-Tensor auf die 3D-Kategorien des Cockpits (Pitch, Roll, Heading).
        Das "Artificial Horizon" Mapping für die UI.
        """
        v = np.array(state_vector)
        # Pitch: Mittlere Resonanz (Energie-Level)
        pitch = float(np.mean(np.abs(v)))
        
        # Roll: Asymmetrie-Gradient (Standardabweichung/Varianz)
        roll = float(np.std(v))
        
        # Heading: Dominanter Phasen-Winkel (Arctan2 der ersten zwei Komponenten)
        if len(v) >= 2:
            heading = float(np.arctan2(v[1], v[0]))
        else:
            heading = 0.049
            
        return {
            "pitch": round(pitch, 3),
            "roll": round(roll, 3),
            "heading": round(heading, 3),
            "status": "IMC_FLYING" if pitch > self.LAMBDA else "VFR_FLYING"
        }

# Singleton Instanz fuer das System
projection_horizon = ProjectionLayer()
