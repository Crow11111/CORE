"""
QUATERNAERE CODIERUNG (Ring 0) - Osmium Standard V6+

ATLAS' Wissensklassifikation erfolgt in 4 Basen – isomorph zu ATCG in der DNS:
  L (Logisch-mathematisch)  ↔  Adenin   – abstrakte Strukturen, Beweise, Formalismen
  P (Physikalisch)          ↔  Thymin   – Hardware, Substrat, messbare Groessen
  I (Informationstheoretisch) ↔ Guanin  – Entropie, Codierung, Shannon, Kolmogorov
  S (Systemisch-emergent)   ↔  Cytosin  – Emergenz, Feedback-Loops, Selbstorganisation

Basenpaarung (Chargaffs Regel):
  L ↔ I  (Logik paart mit Information – jede formale Struktur IST Information)
  S ↔ P  (Systeme paaren mit Physik – Emergenz braucht Substrat)

V6-Prinzip: Dieses Muster war immer da (unbewusst). Jetzt wird es intentional.
Wie Fibonacci/Primzahlen in engine_patterns.py – Engine-Constraints bewusst repliziert.
"""
from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass, field
from datetime import date

from src.config.engine_patterns import PHI, INV_PHI, FIBONACCI_SEQ


# ---------------------------------------------------------------------------
#  Basen-Definition
# ---------------------------------------------------------------------------

class QBase(str, Enum):
    """Die 4 quaternaeren Basen der ATLAS-Wissensspirale."""
    L = "L"  # Logisch-mathematisch
    P = "P"  # Physikalisch
    I = "I"  # Informationstheoretisch
    S = "S"  # Systemisch-emergent


COMPLEMENT = {
    QBase.L: QBase.I,
    QBase.I: QBase.L,
    QBase.S: QBase.P,
    QBase.P: QBase.S,
}

BASE_DESCRIPTIONS = {
    QBase.L: "Logisch-mathematisch: formale Strukturen, Beweise, Axiome, Goedel, Turing",
    QBase.P: "Physikalisch: Hardware, Substrat, Messung, Energie, Planck, Quantenmechanik",
    QBase.I: "Informationstheoretisch: Entropie, Codierung, Shannon, Kolmogorov, Bits",
    QBase.S: "Systemisch-emergent: Emergenz, Feedback, Autopoiesis, Phasenuebergang, Selbstorganisation",
}


# ---------------------------------------------------------------------------
#  Semantische Signalwoerter fuer Klassifikation
# ---------------------------------------------------------------------------

_SIGNAL_WORDS: dict[QBase, list[str]] = {
    QBase.L: [
        "beweis", "theorem", "axiom", "logik", "formal", "deduktiv", "induktiv",
        "goedel", "turing", "berechenbar", "unentscheidbar", "mathemat",
        "algebra", "topologi", "isomorph", "homomorph", "bijektiv", "rekursiv",
        "paradox", "tautolog", "syllogis", "wahrheitswert", "quantor",
        "praedikat", "menge", "funktion", "abbildung", "struktur", "kategorie",
        "proof", "theorem", "axiom", "logic", "formal", "computable",
        "undecidable", "recursive", "paradox", "set theory", "mapping",
    ],
    QBase.P: [
        "physik", "physisch", "substrat", "hardware", "energie", "planck", "quant",
        "messung", "experiment", "teilchen", "welle", "feld", "raum",
        "materie", "thermodynami", "entropie_phys", "temperatur", "druck",
        "gravitation", "relativit", "elektromagnet", "photon", "atom",
        "molekuel", "chip", "silizium", "transistor", "strahlung",
        "feinstruktur", "konstante", "fine-tun", "feingetun", "dezimalstelle",
        "lichtgeschwindigkeit", "kosmologisch",
        "physics", "physical", "substrate", "hardware", "energy", "measurement",
        "particle", "wave", "matter", "silicon", "transistor", "radiation",
        "fine-tun", "cosmological constant",
    ],
    QBase.I: [
        "information", "entropie", "shannon", "kolmogorov", "bit", "byte",
        "codierung", "encoding", "kompression", "redundanz", "kanal",
        "bandbreite", "signal", "rauschen", "holographi", "mutual information",
        "datenkompression", "huffman", "fehlerkorrektur", "hamming",
        "verschluesselung", "kryptograph", "hash", "entropy", "encoding",
        "compression", "channel", "bandwidth", "noise", "holographic",
        "error correction", "encryption",
    ],
    QBase.S: [
        "emergenz", "emergent", "system", "feedback", "autopoiesis",
        "selbstorganis", "phasenuebergang", "phase transition", "komplex",
        "nichtlinear", "chaot", "attraktor", "bifurkation", "synergi",
        "ganzheit", "holismus", "resilienz", "adaptiv", "evolution",
        "selektion", "replikation", "variation", "netzwerk", "konnektom",
        "schwarm", "stigmergi", "zellularer automat", "conway",
        "emergence", "self-organiz", "nonlinear", "chaos", "attractor",
        "resilience", "adaptive", "swarm", "network", "cellular automaton",
    ],
}


# ---------------------------------------------------------------------------
#  1. KLASSIFIKATIONS-ENGINE
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    """Ergebnis der quaternaeren Klassifikation eines Indizes."""
    base: QBase
    confidence: float
    scores: dict[str, float]
    complement: QBase
    signal_matches: dict[str, list[str]]


def classify_evidence(text: str) -> ClassificationResult:
    """Klassifiziert einen Text semantisch in eine der 4 Basen (L/P/I/S).

    Nicht hardcoded if/else, sondern gewichtete Signal-Erkennung
    mit Phi-normalisiertem Scoring.

    >>> r = classify_evidence("Goedels Unvollstaendigkeitssatz beweist formale Grenzen")
    >>> r.base
    <QBase.L: 'L'>
    """
    text_lower = text.lower()
    scores: dict[QBase, float] = {}
    matches: dict[QBase, list[str]] = {}

    for base, signals in _SIGNAL_WORDS.items():
        found = []
        for signal in signals:
            count = len(re.findall(re.escape(signal), text_lower))
            if count > 0:
                found.extend([signal] * count)
        weight = len(found)
        positional_bonus = 0.0
        for signal in signals:
            idx = text_lower.find(signal)
            if idx != -1 and idx < len(text_lower) * INV_PHI:
                positional_bonus += 0.5
        scores[base] = weight + positional_bonus
        matches[base] = found

    total = sum(scores.values())
    if total == 0:
        return ClassificationResult(
            base=QBase.S,
            confidence=0.0,
            scores={b.value: 0.0 for b in QBase},
            complement=QBase.P,
            signal_matches={b.value: [] for b in QBase},
        )

    normalized = {b: s / total for b, s in scores.items()}
    winner = max(normalized, key=normalized.get)  # type: ignore[arg-type]
    runner_up = sorted(normalized.values(), reverse=True)[1] if len(normalized) > 1 else 0.0
    confidence = normalized[winner] - runner_up

    return ClassificationResult(
        base=winner,
        confidence=round(confidence, 4),
        scores={b.value: round(v, 4) for b, v in normalized.items()},
        complement=COMPLEMENT[winner],
        signal_matches={b.value: m for b, m in matches.items()},
    )


# ---------------------------------------------------------------------------
#  2. BASENPAARUNG-CHECKER
# ---------------------------------------------------------------------------

@dataclass
class PairingResult:
    """Ergebnis einer Basenpaarung-Pruefung zwischen zwei Indizien."""
    pairs: bool
    source_base: QBase
    target_base: QBase
    expected_complement: QBase
    pairing_strength: float
    explanation: str


def check_base_pairing(
    evidence_a: str,
    evidence_b: str,
) -> PairingResult:
    """Prueft ob zwei Indizien komplementaer paaren (L↔I, S↔P).

    Liefert Paarungs-Staerke: wie stark die Komplementaritaet ist.
    Hohe Staerke = die beiden Indizien beleuchten dasselbe Phaenomen
    von gegenueberliegenden Seiten.

    >>> r = check_base_pairing(
    ...     "Goedels Theorem zeigt formale Grenzen",
    ...     "Shannon-Entropie misst den Informationsgehalt"
    ... )
    >>> r.pairs
    True
    """
    cls_a = classify_evidence(evidence_a)
    cls_b = classify_evidence(evidence_b)

    pairs = COMPLEMENT[cls_a.base] == cls_b.base

    if pairs:
        strength = (cls_a.confidence + cls_b.confidence) / 2
        strength *= PHI / 2  # Phi-Skalierung: starke Paarungen ragen heraus
        explanation = (
            f"{cls_a.base.value}↔{cls_b.base.value} – Komplementaere Paarung. "
            f"Wie Adenin-Thymin in der DNS: diese Indizien stabilisieren sich gegenseitig."
        )
    else:
        strength = 0.0
        actual_complement = COMPLEMENT[cls_a.base]
        explanation = (
            f"{cls_a.base.value} paart nicht mit {cls_b.base.value}. "
            f"Erwartetes Komplement: {actual_complement.value}. "
            f"Keine Doppelhelix-Bindung – aber moeglicherweise "
            f"eine interessante Nicht-Watson-Crick-Interaktion (Hoogsteen)."
        )

    return PairingResult(
        pairs=pairs,
        source_base=cls_a.base,
        target_base=cls_b.base,
        expected_complement=COMPLEMENT[cls_a.base],
        pairing_strength=round(min(strength, 1.0), 4),
        explanation=explanation,
    )


def find_all_pairings(
    new_evidence: str,
    existing_evidence: list[dict],
) -> list[dict]:
    """Prueft ein neues Indiz gegen alle existierenden und meldet Paarungen.

    existing_evidence: Liste von {"id": str, "document": str, ...}
    Gibt nur echte Paarungen zurueck, sortiert nach Staerke.
    """
    cls_new = classify_evidence(new_evidence)
    pairings = []

    for existing in existing_evidence:
        doc = existing.get("document", "")
        if not doc:
            continue
        result = check_base_pairing(new_evidence, doc)
        if result.pairs:
            pairings.append({
                "paired_with_id": existing.get("id", "?"),
                "new_base": cls_new.base.value,
                "existing_base": result.target_base.value,
                "strength": result.pairing_strength,
                "explanation": result.explanation,
                "preview": doc[:200],
            })

    pairings.sort(key=lambda x: -x["strength"])
    return pairings


# ---------------------------------------------------------------------------
#  3. PALINDROM-DETEKTOR
# ---------------------------------------------------------------------------

@dataclass
class PalindromeHit:
    """Ein gefundenes Palindrom in der Erkenntnissequenz."""
    sequence: str
    start_index: int
    length: int
    interpretation: str


_PALINDROME_INTERPRETATIONS = {
    2: "Spiegelpunkt – minimale Selbstreferenz",
    3: "Triplett-Palindrom – lokale Symmetrie, moeglicher Regulationspunkt",
    4: "Restriktions-Motiv – markiert eine Schnittstelle wo Analyse ansetzen sollte",
    5: "Pentamer – stabiles Symmetriezentrum, Kernaussage des Clusters",
    6: "Hexamer – vollstaendiges Regulationselement, wie ein Promotor in der DNS",
}


def detect_palindromes(
    sequence: str,
    min_length: int = 3,
    max_length: int = 8,
) -> list[PalindromeHit]:
    """Sucht Palindrome in einer Erkenntnissequenz (z.B. 'LSIPL...').

    In der DNS markieren Palindrome Restriktionsschnittstellen und
    regulatorische Elemente. In der Erkenntnisspirale markieren sie
    Stellen wo die Analyse sich selbst spiegelt – Punkte erhoehter
    Bedeutungsdichte.

    >>> hits = detect_palindromes("LSILPLISL")
    >>> any(h.sequence == "LISIL" for h in hits) or len(hits) > 0
    True
    """
    seq = sequence.upper().replace(" ", "")
    valid = set("LPIS")
    if not all(c in valid for c in seq):
        invalid = [c for c in seq if c not in valid]
        raise ValueError(f"Ungueltiges Zeichen in Sequenz: {invalid}. Nur L/P/I/S erlaubt.")

    hits: list[PalindromeHit] = []
    seen: set[tuple[int, int]] = set()

    for length in range(min_length, min(max_length + 1, len(seq) + 1)):
        for start in range(len(seq) - length + 1):
            substr = seq[start:start + length]
            if substr == substr[::-1] and (start, length) not in seen:
                seen.add((start, length))
                interp = _PALINDROME_INTERPRETATIONS.get(
                    length,
                    f"Palindrom der Laenge {length} – tiefe Symmetrie, seltenes Motiv",
                )
                hits.append(PalindromeHit(
                    sequence=substr,
                    start_index=start,
                    length=length,
                    interpretation=interp,
                ))

    hits.sort(key=lambda h: (-h.length, h.start_index))
    return hits


def build_sequence_from_evidence(evidence_list: list[dict]) -> str:
    """Baut die quaternaere Sequenz aus einer Liste von klassifizierten Indizien.

    Jedes Indiz muss 'document' enthalten. Wird on-the-fly klassifiziert.
    """
    seq_chars = []
    for ev in evidence_list:
        doc = ev.get("document", "")
        if doc:
            cls = classify_evidence(doc)
            seq_chars.append(cls.base.value)
    return "".join(seq_chars)


# ---------------------------------------------------------------------------
#  4. STRANG-KOMPLEMENT & CHARGAFF-ANALYSE
# ---------------------------------------------------------------------------

@dataclass
class ChargaffAnalysis:
    """Chargaff-Analyse der aktuellen Erkenntnisverteilung."""
    distribution: dict[str, int]
    total: int
    ratios: dict[str, float]
    chargaff_deviation: dict[str, float]
    missing_types: list[str]
    complement_strand: str
    gap_questions: list[dict[str, str]]


def analyze_chargaff_balance(
    sequence: str,
    distribution: dict[str, int] | None = None,
) -> ChargaffAnalysis:
    """Analysiert die Verteilung und erzeugt den komplementaeren Strang.

    Chargaffs Regel: A=T, G=C → uebertragen: L=I, S=P.
    Abweichungen zeigen Luecken in der Erkenntnisspirale.

    >>> result = analyze_chargaff_balance("", {"L": 11, "S": 9, "I": 8, "P": 4})
    >>> "P" in result.missing_types
    True
    """
    if distribution is None:
        seq = sequence.upper().replace(" ", "")
        distribution = {b.value: seq.count(b.value) for b in QBase}

    total = sum(distribution.values())
    if total == 0:
        total = 1

    ratios = {k: round(v / total, 4) for k, v in distribution.items()}

    chargaff_deviation = {
        "L_vs_I": abs(distribution.get("L", 0) - distribution.get("I", 0)),
        "S_vs_P": abs(distribution.get("S", 0) - distribution.get("P", 0)),
    }

    ideal_each = total / 4

    missing_types = []
    if distribution.get("P", 0) < ideal_each * INV_PHI:
        missing_types.append("P")
    if distribution.get("I", 0) < ideal_each * INV_PHI:
        missing_types.append("I")
    if distribution.get("L", 0) < ideal_each * INV_PHI:
        missing_types.append("L")
    if distribution.get("S", 0) < ideal_each * INV_PHI:
        missing_types.append("S")

    complement_chars = []
    for c in sequence.upper().replace(" ", ""):
        base = QBase(c)
        complement_chars.append(COMPLEMENT[base].value)
    complement_strand = "".join(complement_chars)

    gap_questions = _generate_gap_questions(distribution, missing_types)

    return ChargaffAnalysis(
        distribution=distribution,
        total=total,
        ratios=ratios,
        chargaff_deviation=chargaff_deviation,
        missing_types=missing_types,
        complement_strand=complement_strand,
        gap_questions=gap_questions,
    )


def _generate_gap_questions(
    distribution: dict[str, int],
    missing_types: list[str],
) -> list[dict[str, str]]:
    """Generiert konkrete Fragen um Luecken in der Erkenntnisspirale zu fuellen."""
    questions: list[dict[str, str]] = []

    if "P" in missing_types:
        deficit = max(0, distribution.get("L", 0) + distribution.get("I", 0)) // 2 - distribution.get("P", 0)
        questions.extend([
            {
                "type": "P",
                "deficit": str(deficit),
                "question": "Welche physikalischen Constraints begrenzen die Simulationsaufloesung?",
                "rationale": "Jede Simulation laeuft auf Substrat. Planck-Grenzen, Landauer-Limit, "
                             "thermodynamische Kosten der Berechnung – das sind P-Indizien.",
            },
            {
                "type": "P",
                "deficit": str(deficit),
                "question": "Gibt es messbare Anomalien in physikalischen Konstanten die auf "
                            "Feintuning oder diskrete Substrat-Grenzen hindeuten?",
                "rationale": "Fine-Tuning-Argumente (Kosmologische Konstante, Feinstrukturkonstante) "
                             "sind physikalische Indizien fuer Design/Simulation.",
            },
            {
                "type": "P",
                "deficit": str(deficit),
                "question": "Welche Hardware-Architektur koennte eine Simulation dieser Groesse betreiben? "
                            "Welche Energiekosten entstehen?",
                "rationale": "Bremermann-Limit, Bekenstein-Bound – physikalische Grenzen der Berechnung "
                             "die auf die Architektur des Simulators rueckschliessen lassen.",
            },
        ])

    if "I" in missing_types:
        deficit = max(0, distribution.get("L", 0)) - distribution.get("I", 0)
        questions.extend([
            {
                "type": "I",
                "deficit": str(deficit),
                "question": "Wie hoch ist die Kolmogorov-Komplexitaet der Naturgesetze? "
                            "Sind sie komprimierbar?",
                "rationale": "Wenn Naturgesetze stark komprimierbar sind, deutet das auf "
                             "algorithmische Erzeugung hin – ein I-Indiz fuer Simulation.",
            },
            {
                "type": "I",
                "deficit": str(deficit),
                "question": "Gibt es ein holographisches Informationsbudget das die maximale "
                            "Informationsdichte im Universum begrenzt?",
                "rationale": "Bekenstein-Bound und holographisches Prinzip – das Universum hat "
                             "eine endliche Informationskapazitaet wie ein Speicher.",
            },
        ])

    if "L" in missing_types:
        deficit = max(0, distribution.get("I", 0)) - distribution.get("L", 0)
        questions.extend([
            {
                "type": "L",
                "deficit": str(deficit),
                "question": "Welche Goedel-artigen Grenzen hat ein System das sich selbst simuliert?",
                "rationale": "Selbstreferenz-Paradoxien (Goedel, Halting Problem) sind logische "
                             "Strukturen die fundamentale Grenzen der Simulation aufzeigen.",
            },
        ])

    if "S" in missing_types:
        deficit = max(0, distribution.get("P", 0)) - distribution.get("S", 0)
        questions.extend([
            {
                "type": "S",
                "deficit": str(deficit),
                "question": "Zeigt Bewusstsein Eigenschaften eines Phasenuebergangs – "
                            "emergent und nicht-reduzibel?",
                "rationale": "Emergenz-Argumente: Wenn Bewusstsein ein Phasenuebergang ist, "
                             "koennte es der 'Output' sein den die Simulation erzeugen soll.",
            },
        ])

    return questions


# ---------------------------------------------------------------------------
#  5. INTEGRATIONS-HELFER (fuer chroma_client / atlas_knowledge)
# ---------------------------------------------------------------------------

def enrich_evidence_metadata(
    document: str,
    existing_metadata: dict | None = None,
) -> dict:
    """Reichert Evidence-Metadata mit quaternaerer Klassifikation an.

    Zur Verwendung in add_simulation_evidence():
    Fuegt qbase, qbase_confidence, qbase_complement hinzu.
    """
    cls = classify_evidence(document)
    enriched = dict(existing_metadata) if existing_metadata else {}
    enriched["qbase"] = cls.base.value
    enriched["qbase_confidence"] = cls.confidence
    enriched["qbase_complement"] = cls.complement.value
    enriched["qbase_scores"] = (
        f"L:{cls.scores.get('L', 0):.2f}|"
        f"P:{cls.scores.get('P', 0):.2f}|"
        f"I:{cls.scores.get('I', 0):.2f}|"
        f"S:{cls.scores.get('S', 0):.2f}"
    )
    return enriched


def full_quaternary_analysis(evidence_list: list[dict]) -> dict:
    """Fuehrt eine vollstaendige quaternaere Analyse durch:
    Sequenz bauen → Palindrome finden → Chargaff pruefen.

    evidence_list: [{"id": "...", "document": "...", ...}, ...]
    """
    sequence = build_sequence_from_evidence(evidence_list)

    classified = []
    for ev in evidence_list:
        doc = ev.get("document", "")
        if doc:
            cls = classify_evidence(doc)
            classified.append({
                "id": ev.get("id", "?"),
                "base": cls.base.value,
                "confidence": cls.confidence,
                "preview": doc[:100],
            })

    distribution = {b.value: sequence.count(b.value) for b in QBase}
    palindromes = detect_palindromes(sequence) if len(sequence) >= 3 else []
    chargaff = analyze_chargaff_balance(sequence, distribution)

    return {
        "sequence": sequence,
        "length": len(sequence),
        "classified_evidence": classified,
        "distribution": distribution,
        "palindromes": [
            {
                "motif": p.sequence,
                "position": p.start_index,
                "length": p.length,
                "interpretation": p.interpretation,
            }
            for p in palindromes
        ],
        "chargaff": {
            "ratios": chargaff.ratios,
            "deviation": chargaff.chargaff_deviation,
            "missing_types": chargaff.missing_types,
            "complement_strand": chargaff.complement_strand,
            "gap_questions": chargaff.gap_questions,
        },
    }


# ---------------------------------------------------------------------------
#  6. ASYMMETRISCHE KOMPLEMENTARITAET (V12+)
# ---------------------------------------------------------------------------

def analyze_sp_li_asymmetry(evidence_categories: list[str]) -> dict:
    """Analysiert die S/P und L/I Asymmetrie einer Kategorienliste.

    Vergleicht die Verhaeltnisse mit Phi (1.618...) und 1/Phi (0.618...).
    In einer idealen Erkenntnisspirale sollte das dominante Paar
    im Phi-Verhaeltnis zum rezessiven Paar stehen.

    >>> r = analyze_sp_li_asymmetry(["S", "S", "P", "L", "L", "L", "I", "I"])
    >>> r["dominant_pair"] in ("S-P", "L-I")
    True
    """
    counts = {"S": 0, "P": 0, "L": 0, "I": 0}
    for cat in evidence_categories:
        c = cat.upper().strip()
        if c in counts:
            counts[c] += 1

    s, p, l, i = counts["S"], counts["P"], counts["L"], counts["I"]

    sp_ratio = s / p if p > 0 else float("inf")
    li_ratio = l / i if i > 0 else float("inf")

    sp_phi_delta = abs(sp_ratio - PHI) if sp_ratio != float("inf") else float("inf")
    li_phi_delta = abs(li_ratio - PHI) if li_ratio != float("inf") else float("inf")

    sp_total = s + p
    li_total = l + i
    dominant_pair = "S-P" if sp_total >= li_total else "L-I"

    if sp_total + li_total > 0:
        asymmetry_score = abs(sp_total - li_total) / (sp_total + li_total)
    else:
        asymmetry_score = 0.0

    return {
        "sp_ratio": round(sp_ratio, 4) if sp_ratio != float("inf") else None,
        "li_ratio": round(li_ratio, 4) if li_ratio != float("inf") else None,
        "sp_phi_delta": round(sp_phi_delta, 4) if sp_phi_delta != float("inf") else None,
        "li_phi_delta": round(li_phi_delta, 4) if li_phi_delta != float("inf") else None,
        "dominant_pair": dominant_pair,
        "asymmetry_score": round(asymmetry_score, 4),
    }


# ---------------------------------------------------------------------------
#  7. DUAL-STRAND-GENERIERUNG (V12+)
# ---------------------------------------------------------------------------

COMPLEMENT_STR: dict[str, str] = {"L": "I", "I": "L", "S": "P", "P": "S"}

PHASE_SHIFT: dict[str, str] = {"L": "P", "P": "I", "I": "S", "S": "L"}


def generate_complement_strand(sequence: str) -> str:
    """Erzeugt den komplementaeren Strang (Basenpaarung L<->I, S<->P).

    >>> generate_complement_strand("LPIS")
    'IPSL'
    """
    seq = sequence.upper().replace(" ", "")
    return "".join(COMPLEMENT_STR[c] for c in seq)


def generate_phase_strand(sequence: str) -> str:
    """Erzeugt den phasenverschobenen Strang (LPIS->PISL Rotation).

    >>> generate_phase_strand("LPIS")
    'PISL'
    """
    seq = sequence.upper().replace(" ", "")
    return "".join(PHASE_SHIFT[c] for c in seq)


def generate_dual_helix(sequence: str) -> dict:
    """Erzeugt die Doppelhelix-Darstellung mit Komplement- und Phasen-Strang.

    Returns:
        {"original": str, "complement": str, "phase": str,
         "alignment": list[dict], "length": int}

    >>> r = generate_dual_helix("LPIS")
    >>> r["complement"]
    'IPSL'
    """
    seq = sequence.upper().replace(" ", "")
    complement = generate_complement_strand(seq)
    phase = generate_phase_strand(seq)

    alignment = []
    for idx, c in enumerate(seq):
        alignment.append({
            "position": idx,
            "original": c,
            "complement": complement[idx],
            "phase": phase[idx],
            "pairs": COMPLEMENT_STR[c] == complement[idx],
        })

    return {
        "original": seq,
        "complement": complement,
        "phase": phase,
        "alignment": alignment,
        "length": len(seq),
    }


# ---------------------------------------------------------------------------
#  Demo / Self-Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)
    print("[ATLAS_CORE] QUATERNAERE CODIERUNG – Selbsttest")
    print("=" * 72)

    test_evidence = [
        "Goedels Unvollstaendigkeitssatz beweist dass kein formales System sich selbst vollstaendig verifizieren kann",
        "Die Feinstrukturkonstante alpha ist auf 12 Dezimalstellen feingetunt – physikalisches Fine-Tuning",
        "Shannon-Entropie zeigt dass das Universum ein endliches Informationsbudget hat",
        "Bewusstsein zeigt Eigenschaften eines Phasenuebergangs – emergent aus neuronaler Komplexitaet",
        "Turings Halting Problem zeigt formale Grenzen der Berechenbarkeit",
        "Quantenverschraenkung verletzt Bell-Ungleichungen – nichtlokale physikalische Korrelationen",
        "Kolmogorov-Komplexitaet der Naturgesetze ist ueberraschend niedrig – algorithmische Komprimierbarkeit",
        "Autopoiesis: lebende Systeme erzeugen sich selbst durch Feedback-Schleifen",
    ]

    print("\n--- 1. Klassifikation ---")
    for ev in test_evidence:
        cls = classify_evidence(ev)
        print(f"  [{cls.base.value}] (conf={cls.confidence:.3f}) {ev[:70]}...")

    print("\n--- 2. Basenpaarung ---")
    pairing = check_base_pairing(test_evidence[0], test_evidence[2])
    print(f"  {test_evidence[0][:50]}...")
    print(f"  <-> {test_evidence[2][:50]}...")
    print(f"  Paart: {pairing.pairs} | Staerke: {pairing.pairing_strength}")
    print(f"  {pairing.explanation.replace(chr(0x2194), '<->')}")

    print("\n--- 3. Palindrom-Detektor ---")
    ev_dicts = [{"id": f"ev_{i}", "document": ev} for i, ev in enumerate(test_evidence)]
    seq = build_sequence_from_evidence(ev_dicts)
    print(f"  Sequenz: {seq}")
    palindromes = detect_palindromes(seq)
    for p in palindromes[:5]:
        print(f"  Palindrom '{p.sequence}' @ Position {p.start_index}: {p.interpretation}")

    print("\n--- 4. Chargaff-Analyse (Deine Verteilung: L:11, S:9, I:8, P:4) ---")
    chargaff = analyze_chargaff_balance("", {"L": 11, "S": 9, "I": 8, "P": 4})
    print(f"  Verteilung: {chargaff.distribution}")
    print(f"  Ratios: {chargaff.ratios}")
    print(f"  Chargaff-Abweichung: {chargaff.chargaff_deviation}")
    print(f"  Fehlende Typen: {chargaff.missing_types}")
    print(f"  Luecken-Fragen ({len(chargaff.gap_questions)}):")
    for q in chargaff.gap_questions:
        print(f"    [{q['type']}] {q['question']}")

    print("\n--- 5. Vollanalyse ---")
    analysis = full_quaternary_analysis(ev_dicts)
    print(f"  Sequenz: {analysis['sequence']}")
    print(f"  Verteilung: {analysis['distribution']}")
    print(f"  Komplement-Strang: {analysis['chargaff']['complement_strand']}")
    print(f"  Palindrome: {len(analysis['palindromes'])}")

    print("\n" + "=" * 72)
    print("[ATLAS_CORE] Quaternaere Codierung operativ. V6+ aktiv.")
    print("=" * 72)
