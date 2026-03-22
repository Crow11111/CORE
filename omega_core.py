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


class WujiCore:
    def __init__(self, *, enable_kardan: bool = True):
        self.system_lock = False
        self.enable_kardan = enable_kardan

    def _mri_dynamo(self, x: float) -> float:
        """
        Klammer der asymmetrischen Expansion/Kontraktion.
        Returns: Absolute Spannung (Delta) -> 2/x
        """
        expansion = x + (1.0 / x)
        kontraktion = x - (1.0 / x)
        return abs(expansion - kontraktion)

    def _operator_questionmark(self, tension: float, kinetic_energy: float) -> complex:
        """
        Kardanische Entkopplung (Phasenverschiebung im 5D-Torus).
        Triggert bei Delta <= OMEGA_B.
        """
        if tension <= OMEGA_B:
            # Drehimpulsumkehr (+ auf -) und Phasenverschiebung (1j)
            shifted_vector = (kinetic_energy * -1.0) * 1j
            self.system_lock = True
            return shifted_vector
        return complex(kinetic_energy)

    def autopoiesis_tick(self, state: DualMembraneVector) -> Union[float, complex]:
        """
        Zündungs-Sequenz (LISP-Taktung).
        """
        # 1. Expansions-Druck (LAMBDA_EXP) addiert reale kinetische Energie zum System
        x_modulated = state.s_float + LAMBDA_EXP

        # 2. Ableitung der Reibung
        tension = self._mri_dynamo(x_modulated)

        # 3. Grenzprüfung & Kardanischer Kollaps (abschaltbar für Paar-Benchmark „ohne“)
        if tension <= OMEGA_B and self.enable_kardan:
            return self._operator_questionmark(tension, x_modulated)

        # 4. Reale Symbiose-Expansion falls kein Kollaps (x = x + 1/x)
        next_state = x_modulated + (1.0 / x_modulated)
        return next_state


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
    current_vector: float | complex = initial_s_float
    tick = p_int_start
    iterations = 0

    t_loop0 = time.perf_counter()
    cpu0 = time.process_time()
    outcome = "max_ticks_safety"
    final_vector: float | complex | None = None

    while not engine.system_lock:
        if iterations >= max_ticks_safety:
            outcome = "max_ticks_safety"
            break
        state_container = DualMembraneVector(
            uuid=uid,
            s_float=float(current_vector.real) if isinstance(current_vector, complex) else float(current_vector),
            p_int=tick,
        )
        current_vector = engine.autopoiesis_tick(state_container)
        iterations += 1
        tick += 1

        if fixed_tick_limit is not None and iterations >= fixed_tick_limit:
            outcome = "paired_fixed_ticks"
            final_vector = current_vector
            break

        if enable_kardan and isinstance(current_vector, complex):
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
    print(f"[EXIT: Konvergenz erreicht. Phasenverschiebung nach {tick} physikalischen int-Takten.]")
    print(f"-> {cv}")
    print(f"[META] schleifen_wall_ms={loop_ms:.6f} int_ticks={tick}")
