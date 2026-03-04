#!/usr/bin/env python3
"""
ATLAS 4D State Vector – Validierung aller Schwellwerte und Konstanten.

Validiert:
- Mathematische Konstanten (PHI, INV_PHI, COMP_PHI, SYMMETRY_BREAK, BARYONIC_DELTA)
- Vordefinierte Zustaende (WUJI, ANSAUGEN, VERDICHTEN, ARBEITEN, AUSSTOSSEN)
- Agos-Zyklus-Konsistenz
- Phi-Balance- und Symmetriebruch-Pruefung
- get_current_state() mit Env-Variablen
- Munin-Veto-Override (ring0_state)
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Referenzwerte (exakte Mathematik)
PHI_EXACT = (1 + math.sqrt(5)) / 2
INV_PHI_EXACT = 1 / PHI_EXACT
COMP_PHI_EXACT = 1 - INV_PHI_EXACT


def test_constants() -> list[str]:
    """Validiert mathematische Konstanten."""
    from src.config.atlas_state_vector import PHI, INV_PHI, COMP_PHI, SYMMETRY_BREAK, BARYONIC_DELTA

    errors = []
    # PHI
    if abs(PHI - PHI_EXACT) > 1e-14:
        errors.append(f"PHI: {PHI} != {PHI_EXACT}")
    else:
        print("  PHI = 1.618... OK")

    # INV_PHI = 1/PHI
    if abs(INV_PHI - INV_PHI_EXACT) > 1e-14:
        errors.append(f"INV_PHI: {INV_PHI} != {INV_PHI_EXACT}")
    else:
        print("  INV_PHI = 0.618... OK")

    # COMP_PHI = 1 - INV_PHI
    if abs(COMP_PHI - COMP_PHI_EXACT) > 1e-14:
        errors.append(f"COMP_PHI: {COMP_PHI} != {COMP_PHI_EXACT}")
    else:
        print("  COMP_PHI = 0.382... OK")

    # INV_PHI + COMP_PHI = 1
    if abs(INV_PHI + COMP_PHI - 1.0) > 1e-14:
        errors.append(f"INV_PHI + COMP_PHI != 1: {INV_PHI + COMP_PHI}")
    else:
        print("  INV_PHI + COMP_PHI = 1 OK")

    # SYMMETRY_BREAK (Wuji-Theorie: 0.49/0.51 minimale Asymmetrie)
    if SYMMETRY_BREAK != 0.49:
        errors.append(f"SYMMETRY_BREAK: {SYMMETRY_BREAK} != 0.49")
    else:
        print("  SYMMETRY_BREAK = 0.49 OK")

    # BARYONIC_DELTA (Omega_b = 4.9% kosmologische Dichte)
    if abs(BARYONIC_DELTA - 0.049) > 1e-6:
        errors.append(f"BARYONIC_DELTA: {BARYONIC_DELTA} != 0.049")
    else:
        print("  BARYONIC_DELTA = 0.049 (Omega_b) OK")

    return errors


def test_predefined_states() -> list[str]:
    """Validiert vordefinierte Zustaende gegen ATLAS_4_STRANG_THEORIE."""
    from src.config.atlas_state_vector import (
        WUJI,
        ANSAUGEN,
        VERDICHTEN,
        ARBEITEN,
        AUSSTOSSEN,
    )

    expected = {
        "WUJI": (0.5, 0.0, 0.5, 0),
        "ANSAUGEN": (0.3, 0.2, 0.8, 1),
        "VERDICHTEN": (0.7, 0.5, 0.4, 2),
        "ARBEITEN": (0.2, 0.8, 0.2, 3),
        "AUSSTOSSEN": (0.5, 0.3, 0.6, 4),
    }
    states = [WUJI, ANSAUGEN, VERDICHTEN, ARBEITEN, AUSSTOSSEN]
    names = ["WUJI", "ANSAUGEN", "VERDICHTEN", "ARBEITEN", "AUSSTOSSEN"]
    errors = []

    for name, state in zip(names, states):
        exp = expected[name]
        actual = (state.x_car_cdr, state.y_gravitation, state.z_widerstand, state.w_takt)
        if actual != exp:
            errors.append(f"{name}: {actual} != {exp}")
        else:
            print(f"  {name}: {actual} OK")

    return errors


def test_agos_cycle() -> list[str]:
    """Prueft Agos-Zyklus-Konsistenz (Takt 0-4)."""
    from src.config.atlas_state_vector import WUJI, ANSAUGEN, VERDICHTEN, ARBEITEN, AUSSTOSSEN

    cycle = [WUJI, ANSAUGEN, VERDICHTEN, ARBEITEN, AUSSTOSSEN]
    names = ["WUJI(0)", "ANSAUGEN(1)", "VERDICHTEN(2)", "ARBEITEN(3)", "AUSSTOSSEN(4)"]
    errors = []

    for i, (s, n) in enumerate(zip(cycle, names)):
        if s.w_takt != i:
            errors.append(f"{n}: w_takt={s.w_takt} != {i}")
        else:
            print(f"  Takt {i}: {n} OK")

    return errors


def test_phi_balance() -> list[str]:
    """Prueft is_in_phi_balance()."""
    from src.config.atlas_state_vector import (
        ATLASStateVector,
        INV_PHI,
        COMP_PHI,
        WUJI,
    )

    errors = []
    # Bei INV_PHI sollte True sein
    v_inv = ATLASStateVector(INV_PHI, 0, 0.5, 0)
    if not v_inv.is_in_phi_balance():
        errors.append(f"x={INV_PHI} sollte phi_balance=True liefern")
    else:
        print("  is_in_phi_balance(INV_PHI) OK")

    # Bei COMP_PHI sollte True sein
    v_comp = ATLASStateVector(COMP_PHI, 0, 0.5, 0)
    if not v_comp.is_in_phi_balance():
        errors.append(f"x={COMP_PHI} sollte phi_balance=True liefern")
    else:
        print("  is_in_phi_balance(COMP_PHI) OK")

    # WUJI (0.5) ist NICHT in Phi-Balance (Toleranz 0.05)
    if WUJI.is_in_phi_balance():
        errors.append("WUJI(0.5) sollte phi_balance=False liefern (neutral)")
    else:
        print("  WUJI(0.5) phi_balance=False OK (neutral)")

    return errors


def test_symmetry_broken() -> list[str]:
    """Prueft is_symmetry_broken()."""
    from src.config.atlas_state_vector import ATLASStateVector, SYMMETRY_BREAK

    errors = []
    # Bei y=0.49 sollte True sein
    v = ATLASStateVector(0.5, SYMMETRY_BREAK, 0.5, 0)
    if not v.is_symmetry_broken():
        errors.append(f"y={SYMMETRY_BREAK} sollte symmetry_broken=True liefern")
    else:
        print("  is_symmetry_broken(0.49) OK")

    # Bei y=0 sollte False sein
    v0 = ATLASStateVector(0.5, 0.0, 0.5, 0)
    if v0.is_symmetry_broken():
        errors.append("y=0 sollte symmetry_broken=False liefern")
    else:
        print("  is_symmetry_broken(0) False OK")

    return errors


def test_get_current_state() -> list[str]:
    """Prueft get_current_state() mit Env-Variablen."""
    from src.config.atlas_state_vector import (
        get_current_state,
        WUJI,
        ANSAUGEN,
        VERDICHTEN,
        ARBEITEN,
        AUSSTOSSEN,
    )

    errors = []
    orig_preset = os.environ.get("ATLAS_STATE_PRESET")
    orig_z = os.environ.get("ATLAS_Z_WIDERSTAND")

    try:
        # Default = WUJI
        if "ATLAS_STATE_PRESET" in os.environ:
            del os.environ["ATLAS_STATE_PRESET"]
        if "ATLAS_Z_WIDERSTAND" in os.environ:
            del os.environ["ATLAS_Z_WIDERSTAND"]
        # Munin-Veto zuruecksetzen
        try:
            from src.config.ring0_state import clear_munin_veto
            clear_munin_veto()
        except Exception:
            pass

        s = get_current_state()
        if s.w_takt != WUJI.w_takt or abs(s.x_car_cdr - WUJI.x_car_cdr) > 1e-9:
            errors.append(f"Default sollte WUJI sein: {s}")
        else:
            print("  get_current_state() Default=WUJI OK")

        # Preset ANSAUGEN
        os.environ["ATLAS_STATE_PRESET"] = "ANSAUGEN"
        s = get_current_state()
        if s.w_takt != 1 or abs(s.x_car_cdr - 0.3) > 1e-9:
            errors.append(f"Preset ANSAUGEN: {s}")
        else:
            print("  ATLAS_STATE_PRESET=ANSAUGEN OK")

        # Preset VERDICHTEN
        os.environ["ATLAS_STATE_PRESET"] = "VERDICHTEN"
        s = get_current_state()
        if s.w_takt != 2:
            errors.append(f"Preset VERDICHTEN: w_takt={s.w_takt}")
        else:
            print("  ATLAS_STATE_PRESET=VERDICHTEN OK")

        # Z-Widerstand Override
        os.environ["ATLAS_STATE_PRESET"] = ""
        os.environ["ATLAS_Z_WIDERSTAND"] = "0.9"
        s = get_current_state()
        if abs(s.z_widerstand - 0.9) > 1e-9:
            errors.append(f"ATLAS_Z_WIDERSTAND=0.9: z={s.z_widerstand}")
        else:
            print("  ATLAS_Z_WIDERSTAND=0.9 OK")

    finally:
        if orig_preset is not None:
            os.environ["ATLAS_STATE_PRESET"] = orig_preset
        elif "ATLAS_STATE_PRESET" in os.environ:
            del os.environ["ATLAS_STATE_PRESET"]
        if orig_z is not None:
            os.environ["ATLAS_Z_WIDERSTAND"] = orig_z
        elif "ATLAS_Z_WIDERSTAND" in os.environ:
            del os.environ["ATLAS_Z_WIDERSTAND"]
        try:
            from src.config.ring0_state import clear_munin_veto
            clear_munin_veto()
        except Exception:
            pass

    return errors


def test_munin_veto_override() -> list[str]:
    """Prueft Munin-Veto-Override (ring0_state)."""
    from src.config.atlas_state_vector import get_current_state, WUJI
    from src.config.ring0_state import set_munin_veto, clear_munin_veto, get_munin_veto_override

    errors = []
    orig_preset = os.environ.get("ATLAS_STATE_PRESET")
    try:
        if "ATLAS_STATE_PRESET" in os.environ:
            del os.environ["ATLAS_STATE_PRESET"]
        clear_munin_veto()

        set_munin_veto(0.95)
        s = get_current_state()
        if abs(s.z_widerstand - 0.95) > 1e-9:
            errors.append(f"Munin Veto 0.95: z={s.z_widerstand}")
        else:
            print("  Munin Veto z=0.95 OK")

        clear_munin_veto()
        if get_munin_veto_override() is not None:
            errors.append("clear_munin_veto() sollte None liefern")
        else:
            print("  clear_munin_veto() OK")

    finally:
        clear_munin_veto()
        if orig_preset is not None:
            os.environ["ATLAS_STATE_PRESET"] = orig_preset

    return errors


def test_magnitude() -> list[str]:
    """Prueft magnitude()."""
    from src.config.atlas_state_vector import ATLASStateVector, WUJI

    errors = []
    m = WUJI.magnitude()
    expected = (0.5**2 + 0**2 + 0.5**2 + 0**2) ** 0.5
    if abs(m - expected) > 1e-9:
        errors.append(f"WUJI.magnitude()={m} != {expected}")
    else:
        print("  WUJI.magnitude() OK")

    return errors


def main() -> int:
    print("=== ATLAS 4D State Vector – Validierung ===\n")

    all_errors = []
    sections = [
        ("1. Mathematische Konstanten", test_constants),
        ("2. Vordefinierte Zustaende", test_predefined_states),
        ("3. Agos-Zyklus", test_agos_cycle),
        ("4. Phi-Balance", test_phi_balance),
        ("5. Symmetriebruch", test_symmetry_broken),
        ("6. get_current_state()", test_get_current_state),
        ("7. Munin-Veto-Override", test_munin_veto_override),
        ("8. Magnitude", test_magnitude),
    ]

    for title, fn in sections:
        print(f"\n--- {title} ---")
        errs = fn()
        all_errors.extend(errs)

    print("\n" + "=" * 50)
    if all_errors:
        print("FEHLER:")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print("ALLE TESTS BESTANDEN.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
