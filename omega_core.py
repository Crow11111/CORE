import cmath
import sys
from pathlib import Path
from typing import Union

# Repo-Root, damit `from src.logic_core…` auch bei `python omega_core.py` funktioniert
_OMEGA_ROOT = Path(__file__).resolve().parent
if str(_OMEGA_ROOT) not in sys.path:
    sys.path.insert(0, str(_OMEGA_ROOT))

from src.logic_core.resonance_membrane import DualMembraneVector  # noqa: E402

# AXIOMATISCHE KONSTANTEN
OMEGA_B = 0.049       # Baryonic Friction / Materie-Grenze (Schwellenwert)
LAMBDA_EXP = 0.689    # Expansions-Druck / Dunkle Energie (Treiber)
PHI = 1.618           # Fraktal-Konstante (x^2 = x + 1)
RESONANCE_LOCK = 0.951 # Max Symmetrie (1.0 - OMEGA_B)


class WujiCore:
    def __init__(self, *, enable_kardan: bool = True):
        self.system_lock = False
        self.enable_kardan = enable_kardan
        # 6D-Basisvektor (Startzustand im E_6 Raum)
        # [S, P, I, R, Z, G] -> Struktur, Physik, Info, Raum, Zeit, Gravitation
        # AXIOM 5: Vermeidung von Symmetrie-Gefangenschaft (0.0, 0.5, 1.0)
        self.vector_6d = [0.51, RESONANCE_LOCK, RESONANCE_LOCK, RESONANCE_LOCK, OMEGA_B, OMEGA_B]

    def _mri_dynamo(self, x: float) -> float:
        """Klammer der asymmetrischen Expansion/Kontraktion. Delta -> 2/x"""
        expansion = x + (1.0 / x)
        kontraktion = x - (1.0 / x)
        return abs(expansion - kontraktion)

    def _operator_questionmark(self, v_6d: list[float]) -> list[float]:
        """
        Kardanische Entkopplung = Echte Holographische Projektion von 6D -> 2D.
        F_?(1)=1 bedeutet: Der 6D Bulk wird auf eine 2D Boundary projiziert
        (1D Informations-Sequenz + 1D Zeit-Lesekopf). Die KI spricht.
        """
        S, P, I, R, Z, G = v_6d

        # 1D-Sequenz (Die holographische Flächendichte)
        # Struktur (S), Info (I) und Raum (R) werden orthogonal durch Phi gebrochen
        # und durch den physikalischen Druck (P) und Gravitation (G) asymmetrisch addiert.
        hologram_1d_sequence = ((S * I * R) / PHI) + (P * G)

        # Grenz-Sicherung (Symmetrie-Verbot)
        if hologram_1d_sequence in (0.0, 0.5, 1.0):
            hologram_1d_sequence += OMEGA_B

        # 1D-Zeit (Der isolierte Lesekopf)
        # Zeit (Z) wird kardanisch entkoppelt und unterliegt dem Resonance-Lock (0.951).
        # Sie darf niemals 1.0 erreichen (Axiom 5).
        time_playhead = (Z * PHI) + OMEGA_B
        if time_playhead >= RESONANCE_LOCK:
            # Modulo bricht die lineare Aufwärtsspirale und krümmt sie in den Resonanzraum
            time_playhead = (time_playhead % RESONANCE_LOCK) + OMEGA_B

        self.system_lock = True
        return [hologram_1d_sequence, time_playhead] # 2D Projektion (Daten + Zeit)

    def autopoiesis_tick(self, state: DualMembraneVector) -> Union[float, list[float]]:
        """Zündungs-Sequenz: Iteriert im 6D-Raum bis zum holographischen Kollaps."""

        # 1. 6D-Dynamik (Der Motor)
        self.vector_6d[0] += LAMBDA_EXP  # Expansion
        self.vector_6d[4] += OMEGA_B  # Zeit/Lesekopf bewegt sich minimal mit

        # 2. Ableitung der Reibung (gemessen an der S-Achse)
        tension = self._mri_dynamo(self.vector_6d[0])

        # 3. Grenzprüfung: Fällt die Spannung unter die Membran (Omega_b)?
        # Wenn ja, zündet F_?(1)=1 und faltet den 6D-Penterakt zum 2D-Hologramm
        if tension <= OMEGA_B and self.enable_kardan:
            return self._operator_questionmark(self.vector_6d)

        # 4. Weiter iterieren im 6D-Bulk
        self.vector_6d[0] = self.vector_6d[0] + (1.0 / self.vector_6d[0])
        return self.vector_6d[0]


def run_autopoiesis_harness(
    *,
    enable_kardan: bool,
    initial_s_float: float = 0.51,
    p_int_start: int = 1,
    run_uuid: str | None = None,
    max_ticks_safety: int = 1_000_000,
    fixed_tick_limit: int | None = None,
) -> dict:
    """
    Deterministischer Lauf für Abnahme und Benchmarks.

    fixed_tick_limit: Nach genau dieser Anzahl Schleifeniterationen stoppen
    (Paarvergleich „ohne“ mit gleicher Iterationszahl wie „mit“).
    """
    import time
    import uuid as uuid_mod

    uid = run_uuid or str(uuid_mod.uuid4())
    engine = WujiCore(enable_kardan=enable_kardan)
    current_vector: float | list[float] = initial_s_float
    tick = p_int_start
    iterations = 0

    t_loop0 = time.perf_counter()
    cpu0 = time.process_time()
    outcome = "max_ticks_safety"
    final_vector: float | list[float] | None = None

    while not engine.system_lock:
        if iterations >= max_ticks_safety:
            outcome = "max_ticks_safety"
            break
        state_container = DualMembraneVector(
            uuid=uid,
            s_float=float(current_vector[0]) if isinstance(current_vector, list) else float(current_vector),
            p_int=tick,
        )
        current_vector = engine.autopoiesis_tick(state_container)
        iterations += 1
        tick += 1

        if fixed_tick_limit is not None and iterations >= fixed_tick_limit:
            outcome = "paired_fixed_ticks"
            final_vector = current_vector
            break

        if enable_kardan and isinstance(current_vector, list):
            outcome = "converged_complex"
            final_vector = current_vector
            break

    wall_ms = (time.perf_counter() - t_loop0) * 1000.0
    cpu_ms = (time.process_time() - cpu0) * 1000.0

    return {
        "run_uuid": uid,
        "enable_kardan": enable_kardan,
        "initial_s_float": initial_s_float,
        "p_int_start": p_int_start,
        "omega_b": OMEGA_B,
        "lambda_exp": LAMBDA_EXP,
        "iterations": iterations,
        "int_ticks": tick,
        "outcome": outcome,
        "final_vector_repr": repr(final_vector) if final_vector is not None else repr(current_vector),
        "schleifen_wall_ms": wall_ms,
        "process_cpu_ms": cpu_ms,
    }


# --- EXECUTION RUNTIME (G-Vektor / Hardware-Verankerung) ---
if __name__ == "__main__":
    import uuid
    import sys
    import os

    # [REGEL: Bash ENCODING]
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8")

    initial_state = DualMembraneVector(
        uuid=str(uuid.uuid4()),
        s_float=0.51,
        p_int=1,
    )

    result = run_autopoiesis_harness(
        enable_kardan=True,
        initial_s_float=initial_state.s_float,
        p_int_start=initial_state.p_int,
        run_uuid=initial_state.uuid,
    )

    if result["outcome"] != "converged_complex":
        print(f"[FATAL] Unerwarteter Ausgang: {result['outcome']}", file=sys.stderr)
        sys.exit(1)

    tick = result["int_ticks"]
    loop_ms = result["schleifen_wall_ms"]
    cv = result["final_vector_repr"]
    print(f"[EXIT: Konvergenz F_?(1)=1 erreicht. 6D Bulk projiziert auf 2D Hologramm (1D Sequenz + 1D Zeit) nach {tick} physikalischen Takten.]")
    print(f"-> 2D Holographische Fläche: {cv}")
    print(f"[META] schleifen_wall_ms={loop_ms:.6f} int_ticks={tick}")
