# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
LPIS/PISL Phasenverschiebungs-Modul (V12+)

Implementiert die zyklische Rotation zwischen LPIS- und PISL-Codierung.
LPIS -> PISL: Jede Base rotiert um +1 Position im Zyklus L->P->I->S->L.
PISL -> LPIS: Inverse Rotation (-1).

Die Dualitaet entspricht dem Verhaeltnis von Sense-Strang und Antisense-Strang
in der DNS – derselbe Informationsgehalt, aber phasenverschoben gelesen.
"""
from __future__ import annotations


PISL_MAP: dict[str, str] = {"L": "P", "P": "I", "I": "S", "S": "L"}

LPIS_MAP: dict[str, str] = {"P": "L", "I": "P", "S": "I", "L": "S"}

_VALID_BASES = frozenset("LPIS")


def _validate_sequence(sequence: str) -> str:
    seq = sequence.upper().replace(" ", "")
    invalid = [c for c in seq if c not in _VALID_BASES]
    if invalid:
        raise ValueError(f"Ungueltiges Zeichen in Sequenz: {invalid}. Nur L/P/I/S erlaubt.")
    return seq


def lpis_to_pisl(sequence: str) -> str:
    """Konvertiert eine LPIS-Sequenz in PISL-Codierung (zyklische Rotation +1).

    >>> lpis_to_pisl("LPIS")
    'PISL'
    >>> lpis_to_pisl("LLLL")
    'PPPP'
    """
    seq = _validate_sequence(sequence)
    return "".join(PISL_MAP[c] for c in seq)


def pisl_to_lpis(sequence: str) -> str:
    """Konvertiert eine PISL-Sequenz zurueck in LPIS-Codierung (inverse Rotation).

    >>> pisl_to_lpis("PISL")
    'LPIS'
    >>> pisl_to_lpis(lpis_to_pisl("LSIP"))
    'LSIP'
    """
    seq = _validate_sequence(sequence)
    return "".join(LPIS_MAP[c] for c in seq)


def compute_phase_shift(seq_a: str, seq_b: str) -> int:
    """Berechnet die minimale zyklische Phasenverschiebung zwischen zwei Sequenzen.

    Probiert 0-3 Rotationen durch und gibt die Anzahl der Rotationen zurueck,
    bei der seq_a in seq_b transformiert wird. -1 falls keine Rotation passt.

    >>> compute_phase_shift("LPIS", "PISL")
    1
    >>> compute_phase_shift("LPIS", "LPIS")
    0
    >>> compute_phase_shift("LPIS", "ISLP")
    2
    """
    a = _validate_sequence(seq_a)
    b = _validate_sequence(seq_b)

    if len(a) != len(b):
        return -1

    current = a
    for shift in range(4):
        if current == b:
            return shift
        current = "".join(PISL_MAP[c] for c in current)

    return -1


def sp_stability_check(sequence: str) -> dict:
    """Prueft S-P Abstaende in der Sequenz auf Stabilitaet.

    In einer stabilen Erkenntnisspirale sollte der Abstand zwischen
    S- und P-Basen (Komplementpaare) moeglichst konstant sein.

    Returns:
        {"s_positions": list, "p_positions": list, "sp_distances": list,
         "mean_distance": float, "variance": float, "stable": bool}
    """
    seq = _validate_sequence(sequence)

    s_pos = [i for i, c in enumerate(seq) if c == "S"]
    p_pos = [i for i, c in enumerate(seq) if c == "P"]

    if not s_pos or not p_pos:
        return {
            "s_positions": s_pos,
            "p_positions": p_pos,
            "sp_distances": [],
            "mean_distance": 0.0,
            "variance": 0.0,
            "stable": len(seq) < 2,
        }

    distances = []
    for s in s_pos:
        nearest_p = min(p_pos, key=lambda p: abs(p - s))
        distances.append(abs(nearest_p - s))

    mean_dist = sum(distances) / len(distances) if distances else 0.0
    variance = (
        sum((d - mean_dist) ** 2 for d in distances) / len(distances)
        if distances
        else 0.0
    )

    return {
        "s_positions": s_pos,
        "p_positions": p_pos,
        "sp_distances": distances,
        "mean_distance": round(mean_dist, 4),
        "variance": round(variance, 4),
        "stable": variance < 2.0,
    }


def li_direction_analysis(sequence: str) -> dict:
    """Analysiert L-I Richtungswechsel in der Sequenz.

    Zaehlt wie oft die Sequenz zwischen L und I wechselt. Haeufige Wechsel
    deuten auf starke Logik-Information-Interaktion hin (analoog zu
    Transkriptionsfaktor-Bindungsstellen in der DNS).

    Returns:
        {"l_count": int, "i_count": int, "transitions_l_to_i": int,
         "transitions_i_to_l": int, "total_transitions": int,
         "transition_density": float}
    """
    seq = _validate_sequence(sequence)

    l_count = seq.count("L")
    i_count = seq.count("I")

    l_to_i = 0
    i_to_l = 0

    for idx in range(len(seq) - 1):
        if seq[idx] == "L" and seq[idx + 1] == "I":
            l_to_i += 1
        elif seq[idx] == "I" and seq[idx + 1] == "L":
            i_to_l += 1

    total = l_to_i + i_to_l
    density = total / (len(seq) - 1) if len(seq) > 1 else 0.0

    return {
        "l_count": l_count,
        "i_count": i_count,
        "transitions_l_to_i": l_to_i,
        "transitions_i_to_l": i_to_l,
        "total_transitions": total,
        "transition_density": round(density, 4),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("[MTHO_CORE] LPIS/PISL Phasenverschiebungs-Modul – Selbsttest")
    print("=" * 60)

    print("\n--- lpis_to_pisl ---")
    for seq in ["LPIS", "LLLL", "SIPL", "LSIPL"]:
        print(f"  {seq} -> {lpis_to_pisl(seq)}")

    print("\n--- pisl_to_lpis ---")
    for seq in ["PISL", "PPPP", "LISP"]:
        print(f"  {seq} -> {pisl_to_lpis(seq)}")

    print("\n--- Roundtrip ---")
    test = "LSIPLLISPS"
    converted = lpis_to_pisl(test)
    back = pisl_to_lpis(converted)
    print(f"  Original:  {test}")
    print(f"  PISL:      {converted}")
    print(f"  Zurueck:   {back}")
    print(f"  Roundtrip: {'OK' if back == test else 'FEHLER'}")

    print("\n--- compute_phase_shift ---")
    for a, b in [("LPIS", "PISL"), ("LPIS", "LPIS"), ("LPIS", "ISLP"), ("LPIS", "SLPI")]:
        print(f"  {a} -> {b}: Shift = {compute_phase_shift(a, b)}")

    print("\n--- sp_stability_check ---")
    sp = sp_stability_check("LSIPLLISPS")
    print(f"  Sequenz: LSIPLLISPS")
    print(f"  S-P Distanzen: {sp['sp_distances']}")
    print(f"  Mittel: {sp['mean_distance']}, Varianz: {sp['variance']}")
    print(f"  Stabil: {sp['stable']}")

    print("\n--- li_direction_analysis ---")
    li = li_direction_analysis("LSIPL LISPS")
    print(f"  L->I: {li['transitions_l_to_i']}, I->L: {li['transitions_i_to_l']}")
    print(f"  Dichte: {li['transition_density']}")

    print("\n" + "=" * 60)
    print("[MTHO_CORE] Phasenverschiebungs-Modul operativ.")
    print("=" * 60)
