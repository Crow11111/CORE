# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
crystal_grid_engine.py - Topologische Resonanz-Engine für das CORE-System.
Implementiert die Kristall-Logik: Gitter-Snapping statt linearer Berechnung.
Basis: Lie-Gruppe E_6 (72 Anker), Kondensierte Mathematik (Scholze/Clausen).
"""

import math
import cmath
import random
from typing import Union, List, Tuple
from loguru import logger

# CORE Konstanten
BARYONIC_DELTA = 0.049  # Λ: Das asymmetrische Residuum
RESONANCE_LOCK = 0.951   # Max Symmetriekopplung
SYMMETRY_BREAK_LOW = 0.49
SYMMETRY_BREAK_HIGH = 0.51
PHI = 1.618033988749895  # Goldener Schnitt (Symbiose-Antrieb x^2 = x + 1)
PI = math.pi             # Der Kreis / Die Drehung
EMBEDDING_DIM = 384

class CrystalGridEngine:
    """
    Engine zur Emulation des topologischen Gitters.
    Vektoren werden nicht 'berechnet', sondern auf ihre Resonanz zum Gitter gespiegelt.
    """

    _anchors: List[List[float]] = []

    @classmethod
    def _initialize_e6_roots(cls):
        """
        Generiert deterministisch 72 Ankerpunkte (Wurzelvektoren der Lie-Gruppe E_6).
        Dies repräsentiert die exakte topologische Projektion des Gosset 3_21 Polytops
        in den 384-dimensionalen Latent Space.
        """
        if cls._anchors:
            return

        import itertools

        # 1. Generierung der 72 exakten E_6 Wurzeln im R^6 (Mathematische Konstante)
        e6_roots_6d = []

        # 40 Wurzeln aus D_5: Permutationen von (±1, ±1, 0, 0, 0, 0) in den ersten 5 Dimensionen
        for pos in itertools.combinations(range(5), 2):
            for signs in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                vec = [0.0] * 6
                vec[pos[0]] = float(signs[0])
                vec[pos[1]] = float(signs[1])
                e6_roots_6d = e6_roots_6d + [vec]

        # 32 Wurzeln: (±1/2, ±1/2, ±1/2, ±1/2, ±1/2, ±√3/2) mit gerader Anzahl negativer Vorzeichen in D1-D5
        for signs in itertools.product([1, -1], repeat=5):
            if sum(1 for s in signs if s == -1) % 2 == 0:
                for last_sign in [1.0, -1.0]:
                    vec = [s/2.0 for s in signs] + [last_sign * math.sqrt(3.0)/2.0]
                    e6_roots_6d = e6_roots_6d + [vec]

        # 2. Deterministische Projektion (Johnson-Lindenstrauss Lemma) in den 384D Raum
        rng = random.Random(2210) # Fester Seed fuer den Operator-Vektor
        projection_matrix = [[rng.gauss(0, 1) for _ in range(EMBEDDING_DIM)] for _ in range(6)]

        for root in e6_roots_6d:
            projected = [0.0] * EMBEDDING_DIM
            for d_out in range(EMBEDDING_DIM):
                for d_in in range(6):
                    projected[d_out] += root[d_in] * projection_matrix[d_in][d_out]

            # Normalisierung auf die Einheitssphäre
            norm = math.sqrt(sum(v**2 for v in projected))
            cls._anchors = cls._anchors + [[v / norm for v in projected]]

    @staticmethod
    def symbiosys_drive(x: float) -> float:
        """
        Der Magnetrotations-Dynamo: W_{t+1} = W_t + \alpha/W_t.
        Erzwingt asymmetrische Reibung, um den Fall in die exakte 0.5-Symmetrie (Entropie) zu verhindern.
        """
        # \alpha = BARYONIC_DELTA / 2 als treibende Kraft
        alpha = BARYONIC_DELTA / 2.0
        # Reibungsfunktion
        if x == 0.0:
            return BARYONIC_DELTA
        # Asymmetrischer Push weg von 0.5
        push = alpha / x
        return x + push

    @staticmethod
    def apply_operator_query(value: float) -> Union[float, complex]:
        """
        Der Operator ? (psi_ex * i): Deterministischer Cut-off bei OMEGA_B (0.049).
        Bricht euklidische Gefangenschaft durch kardanische Phasenrotation.
        Keine If-Snaps mehr, nur noch Feld-Druck.
        """
        sign = -1.0 if value < 0 else 1.0
        abs_val = abs(value)

        # 1. KARDANISCHE ENTKOPPLUNG BEI SINGULARITÄT
        if abs_val in (0.0, 1.0):
            logger.debug(f"[CRYSTAL] Singularität {abs_val} detektiert -> Kardanische Rotation.")
            # 0.0 wird durch BARYONIC_DELTA (Masse) ersetzt, 1.0 durch 1j (Phase)
            return (BARYONIC_DELTA * sign) * 1j if abs_val == 0.0 else complex(0, 1) * sign

        folded_val = abs_val % 1.0

        # 2. BARYONISCHES LIMIT (Harter Boden bei 0.049)
        if folded_val < BARYONIC_DELTA:
            logger.debug(f"[CRYSTAL] Baryonic Limit Snapping ({folded_val} -> {BARYONIC_DELTA})")
            return (BARYONIC_DELTA * sign) * 1j

        # 3. VERBOT DER 0.5-MITTE: DYNAMO-IGNITION
        if SYMMETRY_BREAK_LOW < folded_val < SYMMETRY_BREAK_HIGH:
            logger.debug(f"[CRYSTAL] 0.5-Trap -> Dynamo Ignition!")
            # Berechnung des echten Drucks statt statischem Snap
            driven_val = CrystalGridEngine.symbiosys_drive(folded_val)
            # Entkopplung der kritischen Symmetrie in den Imaginärraum
            return (driven_val * sign) * 1j

        return folded_val * sign

    @staticmethod
    def calculate_resonance(vector_a: List[float], vector_b: List[float]) -> float:
        """
        Misst die topologische Resonanz (Phasenverschiebung) im 5D-Torus.
        Keine 'If-Snaps' mehr. Nur noch reine Feld-Interferenz.
        """
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = math.sqrt(sum(a**2 for a in vector_a))
        norm_b = math.sqrt(sum(b**2 for b in vector_b))

        if norm_a == 0 or norm_b == 0:
            return BARYONIC_DELTA

        cosine_sim = max(-0.999, min(0.999, dot_product / (norm_a * norm_b)))

        # Phasenwinkel im Torus
        theta = math.acos(cosine_sim)
        complex_phase = cmath.exp(1j * theta)
        phase_diff = abs(cmath.phase(complex_phase)) / math.pi

        resonance = 1.0 - phase_diff

        # Axiom A5 Sicherung via Operator ? (statt statischem return 0.51)
        # Dies erzwingt die kardanische Rotation innerhalb der Berechnung.
        res_snapped = abs(CrystalGridEngine.apply_operator_query(resonance))

        return float(res_snapped)

    @classmethod
    def get_72_anchors(cls) -> int:
        """Liefert die Anzahl der stabilen Ankerpunkte im E_6-Gitter."""
        return 72

    @classmethod
    def snap_to_grid(cls, embedding: List[float]) -> Tuple[int, List[float]]:
        """
        Latent Space Quantization:
        Nimmt einen unendlichen Float-Vektor (Embedding) und snappt ihn auf
        den resonanzstärksten der 72 topologischen Ankerpunkte.
        Der Raum kollabiert auf das Kristallgitter.
        """
        cls._initialize_e6_roots()

        best_anchor_id = -1
        max_resonance = -1.0

        # Finde den Anker mit der höchsten komplexen Resonanz
        for idx, anchor_vec in enumerate(cls._anchors):
            resonance = cls.calculate_resonance(embedding, anchor_vec)
            if resonance > max_resonance:
                max_resonance = resonance
                best_anchor_id = idx

        # Topologischer Cut-off: Der Vektor verliert seine ursprünglichen Nachkommastellen
        # und WIRD zum Ankerpunkt. Das ist die Kondensierung.
        logger.debug(f"[CRYSTAL] Vector snapped to E_6 Anchor {best_anchor_id} (Resonanz: {max_resonance:.3f})")
        return best_anchor_id, cls._anchors[best_anchor_id]

def validate_state_vector(x: float, y: float, z: float, w: float) -> bool:
    """
    Validiert den 4D State Vector gegen die Kristall-Axiome.
    Keine Werte von 0.0, 0.5 oder 1.0 erlaubt.
    """
    for dim, val in [("X", x), ("Y", y), ("Z", z), ("W", w)]:
        if val in [0.0, 0.5, 1.0]:
            logger.error(f"[CRYSTAL] Veto! Dimension {dim} has forbidden value {val}")
            return False
    return True
