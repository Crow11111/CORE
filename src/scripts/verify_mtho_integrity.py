#!/usr/bin/env python3
"""
MTHO INTEGRITY VERIFIER
Prueft ob die MTHO-Genesis korrekt geladen wird und die harte Abhaengigkeit besteht.
"""
import sys
import os

# Pfad erweitern um src zu finden
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def verify_mtho():
    print("[INIT] Starte MTHO Integritaets-Pruefung...")

    # 1. Pruefe Core Import
    try:
        import src.mtho_core
        print("[OK] src.mtho_core gefunden.")
    except ImportError as e:
        print(f"[FAIL] CRITICAL: src.mtho_core nicht importierbar! {e}")
        sys.exit(1)

    # 2. Pruefe State Vector (und damit die harte Abhaengigkeit)
    try:
        from src.config.atlas_state_vector import MTHO_BASES, BARYONIC_DELTA, M_VALUE
        print("[OK] src.config.atlas_state_vector geladen.")
    except ImportError as e:
        print(f"[FAIL] CRITICAL: atlas_state_vector Import fehlgeschlagen! {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] CRITICAL: Fehler beim Laden von atlas_state_vector: {e}")
        sys.exit(1)

    # 3. Pruefe Bases Integritaet
    expected_bases = {'M', 'T', 'H', 'O'}
    found_bases = set(MTHO_BASES.keys())
    
    if found_bases != expected_bases:
        print(f"[FAIL] MTHO Bases korrupt! Erwartet {expected_bases}, Gefunden {found_bases}")
        sys.exit(1)
    else:
        print("[OK] MTHO Bases vollstaendig (M, T, H, O).")

    # 4. Pruefe Werte
    if M_VALUE != 2:
        print(f"[FAIL] M_VALUE inkonsistent! Erwartet 2, ist {M_VALUE}")
        sys.exit(1)
    
    if BARYONIC_DELTA != 0.049:
        print(f"[FAIL] BARYONIC_DELTA inkonsistent! Erwartet 0.049, ist {BARYONIC_DELTA}")
        sys.exit(1)

    print("\n" + "="*40)
    print("MTHO INTEGRITY: VERIFIED")
    print("="*40)
    return True

if __name__ == "__main__":
    verify_mtho()
