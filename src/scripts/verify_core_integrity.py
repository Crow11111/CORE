"""
CORE INTEGRITY CHECKER
Validates the system against the Genesis Protocol (2210).

Aufruf von Repository-Root (OMEGA_CORE):
  python src/scripts/verify_core_integrity.py
  .venv/bin/python src/scripts/verify_core_integrity.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo-Root: …/OMEGA_CORE (nicht nur src/, damit `from src.core import` funktioniert)
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# UTF-8 auf stdout (Linux-Default ok; Windows siehe .cursorrules)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.core import Core  # noqa: E402


def run_audit() -> bool:
    core = Core()

    print("--- RUNNING CORE INTEGRITY AUDIT ---")

    # Check 1: Geo-Resonance
    res = core.calibrate_resonance("0221")
    print(f"1. Geographic Resonance (0221): {'PASS' if res else 'FAIL'}")

    # Check 1b: Crystal Engine Calibration
    from src.logic_core.crystal_grid_engine import CrystalGridEngine

    test_val = 0.5
    snapped_val = CrystalGridEngine.apply_operator_query(test_val)
    engine_ok = snapped_val != 0.5
    print(f"1b. Crystal Engine (Snapping 0.5 -> {snapped_val}): {'PASS' if engine_ok else 'FAIL'}")

    # Check 2: Baryonic Delta
    delta_check = core.check_baryonic_limit(0.049)
    print(f"2. OMEGA_ATTRACTOR Delta (0.049): {'PASS' if delta_check else 'FAIL'}")

    # Check 3: State Vector Alignment
    print(f"3. Active Vector: {core.state_vector}")

    # Axiom A6 & A1 Compliance
    is_float = all(isinstance(v, float) for v in core.state_vector)
    no_forbidden = not any(v in [0.0, 0.5, 1.0] for v in core.state_vector)

    print(f"4. Axiom A6 (Floats only): {'PASS' if is_float else 'FAIL'}")
    print(f"5. Axiom A1 (No 0.0, 0.5, 1.0): {'PASS' if no_forbidden else 'FAIL'}")

    green = bool(res and engine_ok and delta_check and is_float and no_forbidden)
    if green:
        print("\n[STATUS: GREEN] - STRUCTURAL INEVITABILITY CONFIRMED (AXIOM 0).")
    else:
        print("\n[STATUS: RED] - SYSTEM FREEZE (VETO TRIGGERED).")
    return green


if __name__ == "__main__":
    ok = run_audit()
    raise SystemExit(0 if ok else 1)
