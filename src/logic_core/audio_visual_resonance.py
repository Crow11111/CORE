# -*- coding: utf-8 -*-
# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
Audio/Visual Sensor-Topologie (CONCEPT_AUDIO_VISUAL_MASTER V8).

Zwei-Domänen-Theorie:
  Beobachtungs-Domäne: X_t Akkumulator darf 0.0 annehmen (Stille).
  Resonanz-Domäne: R_t ∈ (0.049, 0.951) offen im Inneren; Grenzen asymptotisch
  über tanh — keine if/else-Heiler, kein min/max-Clamping auf R_t.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.logic_core.crystal_grid_engine import (
    BARYONIC_DELTA,
    EMBEDDING_DIM,
    PHI,
    RESONANCE_LOCK,
)

# Kanonische Spreizung der tanh-Projektion (0.951 − 0.049 = 0.902)
_RESONANCE_SPAN = RESONANCE_LOCK - BARYONIC_DELTA
_INV_PHI = 1.0 / PHI


def accumulate_stimulus_observation(x_prev: float, s_raw: float, phi: float = PHI) -> float:
    """
    Beobachtungs-Domäne: X_t = X_{t-1} / Φ + S_raw.

    S_raw darf 0.0 sein; bei fortlaufender Stille konvergiert X_t → 0.0.
    """
    return (x_prev * (1.0 / phi)) + s_raw


def project_observation_to_resonance(x_t: float) -> float:
    """
    Resonanz-Domäne: R_t = 0.049 + 0.902 · tanh(X_t).

    Rein analytisch; asymptotisch R_t → 0.049 bei Stille, R_t → 0.951 bei großem X_t.
    """
    return BARYONIC_DELTA + _RESONANCE_SPAN * math.tanh(x_t)


def coupling_factor(r_t: float) -> float:
    """K = R_t (Konzept V8)."""
    return r_t + 0.0


def focus_intensity_wf(k: float, phi: float = PHI) -> float:
    """W_f = K^Φ, K aus Resonanz-Domäne."""
    return k**phi


def interval_spread_observation(base_interval: float, r_t: float, phi: float = PHI) -> float:
    """
    Kamera-/Sample-Intervall-Spreizung (Beobachtungs-Skalierung):
    I_v = BaseInterval · Φ^(0.951 − R_t).
    """
    return base_interval * (phi ** (RESONANCE_LOCK - r_t))


def build_resonance_embedding_probe(r_t: float) -> list[float]:
    """
    Deterministischer 384-D-Probekörper aus R_t für Gitter-Quantisierung (Gleis B).

    Stetig in r_t; keine harten Domänen-Weichen.
    """
    out: list[float] = []
    for k in range(EMBEDDING_DIM):
        phase = BARYONIC_DELTA + float(k) * _INV_PHI * 0.01
        out.append(r_t * (PHI ** (k % 11)) * math.sin(phase))
    return out


@dataclass
class SensorStimulusPipeline:
    """
    Ein Takt: S_raw einlesen → X_t aktualisieren → R_t projizieren.
    x_accumulator lebt in der Beobachtungs-Domäne (0.0 erlaubt).
    """

    phi: float = PHI
    x_accumulator: float = field(default=0.0)

    def tick(self, s_raw: float) -> tuple[float, float]:
        """Gibt (X_t, R_t) nach diesem Schritt zurück."""
        self.x_accumulator = accumulate_stimulus_observation(
            self.x_accumulator, s_raw, self.phi
        )
        r_t = project_observation_to_resonance(self.x_accumulator)
        return self.x_accumulator, r_t

    def resonance_now(self) -> float:
        """R_t aus aktuellem Akkumulator (ohne neuen Stimulus)."""
        return project_observation_to_resonance(self.x_accumulator)
