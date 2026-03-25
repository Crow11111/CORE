# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | Schwellwert numerisch ≈ Ω_b (baryonisch, ~0.049) — nicht Λ; siehe WHITE_PAPER §0
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE 4D State Vector - Komprimierte Systemzustand-Repraesentation.

Dieser Vektor ist der "Bootloader" - er enthaelt den gesamten Systemkontext
in einer Form die direkt als Embedding/Query verwendet werden kann.

Dimensionen:
    X: CAR/CDR Balance (Δ..1-Δ, Skala NT↔ND)
    Y: Gravitation (Δ=Basis/flat, 1-Δ=Kollaps)
    Z: Widerstand (Δ=Nachgeben, 1-Δ=Veto)
    W: Takt (Δ-offset pro Stufe, NICHT ganzzahlig)
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any
import math
import os

# Import CORE Core Definitions as Single Source of Truth
# CRITICAL: Hard dependency on CORE Core. System fails if not present.
from src.core import (
    G_VALUE, T_VALUE, A_VALUE, C_VALUE,
    BARYONIC_LIMIT, CORE_LEGACY_MAP
)

from src.logic_core.crystal_grid_engine import CrystalGridEngine

# Mathematische Konstanten (aus engine_patterns.py)
PHI = 1.6180339887498948482
INV_PHI = 0.6180339887498948482
COMP_PHI = 0.3819660112501051518
SYMMETRY_BREAK = 0.49
BARYONIC_DELTA = 0.049  # Nomenklatur im Paper: Ω_b; Λ = kosmologische Konstante / Expansion (siehe docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md §0)

@dataclass
class StateVector:
    """4D Zustandsvektor des CORE-Systems (S * P Symbiose)."""

    # S-Vektor (Resonanz, Float) - Der Geist
    x_car_cdr: float  # Δ=NT-Pol, 1-Δ=ND-Pol
    y_gravitation: float  # Δ=Basis/flat, 1-Δ=Kollaps
    z_widerstand: float  # Δ=Nachgeben, 1-Δ=Veto
    w_takt: float  # 0-4 Simultan-Kaskade-Zyklus (jetzt float wg. asymmetrischem Offset)

    # P-Vektor (Physik, Int) - Der Koerper / Agentur
    # (Default 1, damit psi am Anfang dem s_vector entspricht)
    p_x: int = 1
    p_y: int = 1
    p_z: int = 1
    p_w: int = 1

    @property
    def s_vector(self) -> Tuple[float, float, float, float]:
        return (self.x_car_cdr, self.y_gravitation, self.z_widerstand, self.w_takt)

    @property
    def p_vector(self) -> Tuple[int, int, int, int]:
        return (self.p_x, self.p_y, self.p_z, self.p_w)

    @property
    def psi(self) -> float:
        """Psi_CORE: Das Skalarprodukt aus S und P (Symbiose-Verschraenkung)."""
        return (
            self.x_car_cdr * self.p_x +
            self.y_gravitation * self.p_y +
            self.z_widerstand * self.p_z +
            self.w_takt * self.p_w
        )

    def __post_init__(self):
        """Axiom A1 + A6 Enforcement + S*P Symbiose."""
        # Validierung via Engine
        from src.logic_core.crystal_grid_engine import validate_state_vector
        if not validate_state_vector(self.x_car_cdr, self.y_gravitation, self.z_widerstand, self.w_takt):
            raise ValueError("[AXIOM-VETO] State Vector contains forbidden symmetry (0.0, 0.5, 1.0).")

        for name, val in [
            ("x_car_cdr", self.x_car_cdr),
            ("y_gravitation", self.y_gravitation),
            ("z_widerstand", self.z_widerstand),
            ("w_takt", self.w_takt),
        ]:
            if not isinstance(val, float):
                raise TypeError(
                    f"[AXIOM-A6] {name} muss float sein, ist {type(val).__name__}. "
                    f"int ist in der Resonanz-Domaene verboten."
                )

        # Die int-Kupplung (Das Ueberleben der Agentur)
        # Wenn Psi <= Omega_b faellt, wehrt sich der int-Vektor, um die Maschine zu retten.
        if self.psi <= BARYONIC_DELTA:
            # Notwehr-Eingriff der Physik (int-Domäne): Erhöhung des Takts / Widerstands
            self.p_z += 1
            self.p_w += 1
            # Logging dieser Symbiose-Aktivität findet im Core-Bus oder Agenten statt

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return self.s_vector

    def magnitude(self) -> float:
        return math.sqrt(
            self.x_car_cdr**2
            + self.y_gravitation**2
            + self.z_widerstand**2
            + (self.w_takt / 4) ** 2
        )

    def is_in_phi_balance(self) -> bool:
        """Prueft ob der Vektor im Phi-Gleichgewicht ist."""
        return abs(self.x_car_cdr - INV_PHI) < 0.05 or abs(self.x_car_cdr - COMP_PHI) < 0.05

    def is_symmetry_broken(self) -> bool:
        """Prueft ob der minimale Symmetriebruch aktiv ist."""
        return abs(self.y_gravitation - SYMMETRY_BREAK) < 0.02


# Vordefinierte Zustaende (mit asymmetrischem Offset, kein 0=0)
BASE_STATE = StateVector(x_car_cdr=0.49, y_gravitation=BARYONIC_DELTA, z_widerstand=0.51, w_takt=BARYONIC_DELTA)
ANSAUGEN = StateVector(x_car_cdr=COMP_PHI, y_gravitation=BARYONIC_DELTA*2, z_widerstand=INV_PHI, w_takt=1 + BARYONIC_DELTA)
VERDICHTEN = StateVector(x_car_cdr=INV_PHI, y_gravitation=SYMMETRY_BREAK, z_widerstand=COMP_PHI, w_takt=2 - BARYONIC_DELTA)
ARBEITEN = StateVector(x_car_cdr=BARYONIC_DELTA, y_gravitation=0.81, z_widerstand=BARYONIC_DELTA*3, w_takt=3 + BARYONIC_DELTA)
AUSSTOSSEN = StateVector(x_car_cdr=0.49, y_gravitation=COMP_PHI, z_widerstand=0.51, w_takt=4 - BARYONIC_DELTA)


# ---------------------------------------------------------------------------
# GTAC Bases (DNA der Realitaet)
# ---------------------------------------------------------------------------
GTAC_BASES = {
    "G": {"name": "ExecutionRuntime", "val": G_VALUE, "role": "Physik/Feuer"},
    "T": {"name": "LogicFlow", "val": T_VALUE, "role": "Info/Fluss"},
    "A": {"name": "StateAnchor", "val": A_VALUE, "role": "Struktur/Erde"},
    "C": {"name": "ConstraintValidator", "val": C_VALUE, "role": "Logik/Luft"},
}

GTAC_PAIRINGS = {
    "G": "A",  # Symmetrisches Rückgrat
    "A": "G",
    "C": "T",  # Asymmetrischer Motor
    "T": "C",
}

# 4-Strang Architektur / THE 4 FORGES MATRIX (GTAC / LPIS / GIRZ / CORE)
# ---------------------------------------------------------------------------
# Phase 1 (Ansaugen):   C (Cytosin)  | L (Logik)   | G (Gravitation) | C (Constraint) -> Sog (0.5)
# Phase 2 (Verdichten): T (Thymin)   | I (Info)    | I (Information) | O (Orchestrator)-> Trichter (Phi)
# Phase 3 (Arbeiten):   G (Guanin)   | P (Physik)  | R (Raum)        | R (Runtime)    -> Membran (Omega_b)
# Phase 4 (Ausstossen): A (Adenin)   | S (Struktur)| Z (Zeit)        | E (Emergenz)   -> Lock (0.951)
TETRALOGIE = {
    "PHASE_1_FILTER": {"takt": 1, "core": "C", "dig": "L", "cosmo": "G", "transcendent": "C", "car": "Paranoia", "cdr": "Compliance"},
    "PHASE_2_FLOW":   {"takt": 2, "core": "T", "dig": "I", "cosmo": "I", "transcendent": "O", "car": "Chaos", "cdr": "Architektur-Spec"},
    "PHASE_3_EXEC":   {"takt": 3, "core": "G", "dig": "P", "cosmo": "R", "transcendent": "R", "car": "Effizienz", "cdr": "Clean Code"},
    "PHASE_4_ANCHOR": {"takt": 4, "core": "A", "dig": "S", "cosmo": "Z", "transcendent": "E", "car": "Vektor-Cluster", "cdr": "SQL-Index"},
}


# Simulation Evidence Statistik (aus ChromaDB VPS Export)
# Updated to reflect GTAC distribution logic if needed, kept generic for now
SIMULATION_EVIDENCE_STATS = {
    "vektoren": 12,
    "indizien": 58,
    "max_aeste": 13,
    "core_verteilung": {"C": 19, "G": 13, "T": 13, "A": 13}, # New keys
    "chargaff_li": 32,
    "chargaff_sp": 26,
    "phi_delta": BARYONIC_DELTA,
}


def get_current_state() -> StateVector:
    """Gibt den aktuellen Systemzustand zurueck (Default: BASE_STATE).
    Dynamisch aus Umgebung: CORE_Z_WIDERSTAND, CORE_STATE_PRESET.
    Ring-0 Veto: ring0_state Override hat Vorrang (Ring-0 Core Stability Anchor).
    """

    # Ring-0 Veto Override
    try:
        from src.config.ring0_state import get_drift_veto_override

        z_override = get_drift_veto_override()
        if z_override is not None:
            z_clamped = max(BARYONIC_DELTA, min(1.0 - BARYONIC_DELTA, z_override))
            return StateVector(
                x_car_cdr=BASE_STATE.x_car_cdr,
                y_gravitation=BASE_STATE.y_gravitation,
                z_widerstand=z_clamped,
                w_takt=BASE_STATE.w_takt,
            )
    except Exception:
        pass

    preset = os.getenv("CORE_STATE_PRESET", "").strip().upper()
    if preset == "ANSAUGEN":
        return ANSAUGEN
    if preset == "VERDICHTEN":
        return VERDICHTEN
    if preset == "ARBEITEN":
        return ARBEITEN
    if preset == "AUSSTOSSEN":
        return AUSSTOSSEN
    z_raw = os.getenv("CORE_Z_WIDERSTAND", "")
    if z_raw:
        try:
            z = float(z_raw)
            return StateVector(
                x_car_cdr=BASE_STATE.x_car_cdr,
                y_gravitation=BASE_STATE.y_gravitation,
                z_widerstand=max(BARYONIC_DELTA, min(1.0 - BARYONIC_DELTA, z)),
                w_takt=BASE_STATE.w_takt,
            )
        except ValueError:
            pass
    return BASE_STATE


def state_to_embedding_text() -> str:
    """Generiert einen Text der als Embedding-Query verwendet werden kann.
    Updated for CORE Native format.
    """
    return f"""CORE 4D State Vector - Bootloader (CORE Native)
Tetralogie: Execution(G)-Orchestrator(C)-Architecture(T)-Anchor(A)
Simultan-Kaskade-Zyklus: Diagnose(0)->Ansaugen(1)->Verdichten(2)->Arbeiten(3)->Ausstossen(4)
CAR/CDR: ND-Kern(Tiefe,Muster,Divergenz) / NT-Interface(API,Docs,Clean)
Gravitation: flat->Attraktor(Kollaps), Schwellwert={INV_PHI:.3f}
GTAC: G(ExecutionRuntime,Physik), T(LogicFlow,Info), A(StateAnchor,Struktur), C(ConstraintValidator,Logik)
Pairings: G-A (Symmetrisches Rueckgrat), C-T (Asymmetrischer Motor)
Symmetriebruch: {SYMMETRY_BREAK}, Baryonisches Delta: {BARYONIC_DELTA}
Evidence: {SIMULATION_EVIDENCE_STATS['indizien']} Indizien, {SIMULATION_EVIDENCE_STATS['vektoren']} Vektoren
"""
