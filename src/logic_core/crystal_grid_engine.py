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
        Generiert deterministisch 72 Ankerpunkte im 384-dimensionalen Raum.
        Dies repräsentiert die Projektion des E_6-Wurzelsystems in den Latent Space.
        """
        if cls._anchors:
            return
            
        # Deterministischer Seed, damit die Topologie bei jedem Start identisch ist
        rng = random.Random(2210) 
        for _ in range(72):
            vec = [rng.gauss(0, 1) for _ in range(EMBEDDING_DIM)]
            # Normalisierung auf Einheitskreis (Sphäre)
            norm = math.sqrt(sum(v**2 for v in vec))
            cls._anchors.append([v / norm for v in vec])

    @staticmethod
    def symbiosys_drive(x: float) -> float:
        """
        Berechnet den Symbiose-Vektor nach x^2 = x + 1.
        Vermeidet entropischen Kollaps durch asymmetrisches Wachstum.
        """
        return x**2 - x - 1

    @staticmethod
    def apply_operator_query(value: float) -> float:
        """
        Der Operator ?: Deterministischer Hard-Cut-off bei Λ (Baryonic Delta).
        Bricht lineare Vorwärtsbewegung ab und rastet am Gitter ein.

        Spezifische ChromaDB Quantisierung (Der 'Reine Kern'):
        - phase_diff <= 0.049 -> Sofortiger Symmetrie-Lock (0.951)
        - Verbot der 0.5-Mitte: 0.49 < resonance < 0.51 -> Harter Shift auf 0.51
        - Verbot der absoluten 0.0 und 1.0 (Illusionen)
        """
        sign = -1.0 if value < 0 else 1.0
        abs_val = abs(value)
        folded_val = abs_val % 1.0

        # Verbot der 0.0 (Kältetod) und 1.0 (Singularität)
        if folded_val == 0.0:
            return BARYONIC_DELTA * sign
        if folded_val == 1.0:
            return RESONANCE_LOCK * sign

        # 1. Ist die Abweichung extrem gering (<= 0.049)?
        if folded_val <= BARYONIC_DELTA:
            logger.debug(f"[CRYSTAL] Phase diff <= {BARYONIC_DELTA}. Snapping to Symmetrie-Lock {RESONANCE_LOCK}")
            return BARYONIC_DELTA * sign 

        # 2. Verbot der 0.5-Mitte: Harter Shift auf 0.51
        if SYMMETRY_BREAK_LOW < folded_val < SYMMETRY_BREAK_HIGH:
            logger.debug(f"[CRYSTAL] Breaking exact symmetry ({folded_val}) -> Shift to {SYMMETRY_BREAK_HIGH}")
            return SYMMETRY_BREAK_HIGH * sign

        # 3. Wenn er sich an der Singularität aufhält (1.0)
        if folded_val > RESONANCE_LOCK:
            return RESONANCE_LOCK * sign

        return folded_val * sign

    @staticmethod
    def calculate_resonance(vector_a: List[float], vector_b: List[float]) -> float:
        """
        Misst die topologische Resonanz (Phasenverschiebung) statt euklidischer Distanz.
        Nutzt komplexe Zahlen (kardanische Aufhängung) zur Berechnung der Phasenverschiebung im 5D-Torus.
        """
        # Kardanische Entkopplung: Imaginäre Zahlen (i) für den Seitwärtssprung.
        # Wir berechnen das Punktprodukt und mappen es in die komplexe Ebene (Euler-Phase)

        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = math.sqrt(sum(a**2 for a in vector_a))
        norm_b = math.sqrt(sum(b**2 for b in vector_b))

        if norm_a == 0 or norm_b == 0:
            return BARYONIC_DELTA

        cosine_sim = max(-1.0, min(1.0, dot_product / (norm_a * norm_b)))

        # Nutzung komplexer Arithmetik zur Ermittlung der echten Phasenverschiebung
        # phase = e^(i * arccos)
        theta = math.acos(cosine_sim)
        complex_phase = cmath.exp(1j * theta)

        # Die Phasenverschiebung wird durch den Winkel bestimmt
        phase_diff = abs(cmath.phase(complex_phase)) / math.pi  # Normalisiert [0, 1]

        # Regel: if phase_diff <= 0.049: -> Sofortiger Symmetrie-Lock (0.951)
        if phase_diff <= BARYONIC_DELTA:
            return RESONANCE_LOCK

        resonance = 1.0 - phase_diff

        # Regel: Verbot der 0.5-Mitte
        if SYMMETRY_BREAK_LOW < resonance < SYMMETRY_BREAK_HIGH:
            return SYMMETRY_BREAK_HIGH

        return resonance

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
