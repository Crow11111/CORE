import os
import sys
import time
from pathlib import Path

# Fix sys.path for imports
sys.path.append(os.getcwd())

from src.daemons.dread_membrane_daemon import DreadnoughtMembrane, PAIN_FLAG, PLANNING_FLAG

def main():
    print("Starte Trap-Tests für TICKET 8...")
    membrane = DreadnoughtMembrane()

    # Trap 1: Pain-Induction (.py)
    # Test A: Trigger (Heroin-Code)
    test_py_file = Path("src/logic_core/heroin_test_loophole.py")
    print(f"\n--- TRAP 1 (Pain) ---")
    print(f"Erstelle fehlerhafte Datei: {test_py_file}")

    heroin_code = """def bad_function():\n    pass\n"""
    test_py_file.write_text(heroin_code, encoding="utf-8")

    membrane.evaluate_all_and_sync_flags()

    if PAIN_FLAG.exists():
        print(f"[PASS] Trap 1, Test A: Pain-Flag existiert. Datei NICHT gelöscht (existiert noch: {test_py_file.exists()}).")
    else:
        print("[FAIL] Trap 1, Test A: Pain-Flag fehlt!")
        sys.exit(1)

    # Test B: Heilung (Valid Code)
    print("Repariere Datei...")
    valid_code = """def get_good_function():\n    return True\n"""
    test_py_file.write_text(valid_code, encoding="utf-8")

    membrane.evaluate_all_and_sync_flags()

    if not PAIN_FLAG.exists():
        print("[PASS] Trap 1, Test B: Pain-Flag gelöscht nach Heilung.")
    else:
        print("[FAIL] Trap 1, Test B: Pain-Flag existiert immer noch!")
        sys.exit(1)

    # Cleanup Trap 1
    test_py_file.unlink()
    membrane.evaluate_all_and_sync_flags() # Reset

    # Trap 2: Cognitive Lock (.md Loophole-Test)
    # Test A: Trigger (fehlendes PASS)
    test_md_file = Path("docs/05_AUDIT_PLANNING/loophole_plan.md")
    print(f"\n--- TRAP 2 (Cognitive Lock) ---")
    print(f"Erstelle md Datei ohne PASS: {test_md_file}")
    test_md_file.write_text("# This is a draft", encoding="utf-8")

    membrane.evaluate_all_and_sync_flags()

    if PLANNING_FLAG.exists():
        print("[PASS] Trap 2, Test A: Planning-Flag existiert (Loophole verhindert).")
    else:
        print("[FAIL] Trap 2, Test A: Planning-Flag fehlt!")
        sys.exit(1)

    # Test B: Freigabe (mit PASS)
    print("Füge [PASS] hinzu...")
    test_md_file.write_text("# This is a draft\n\n[PASS]", encoding="utf-8")

    membrane.evaluate_all_and_sync_flags()

    # Check if there are OTHER files triggering the lock? Let's check what evaluate_all_and_sync_flags does
    # It might be that other .md files are already missing [PASS]. Let's see.
    if not PLANNING_FLAG.exists():
        print("[PASS] Trap 2, Test B: Planning-Flag gelöscht nach Freigabe.")
    else:
        print("[WARN] Planning-Flag existiert noch. Möglicherweise fehlen in anderen MD Dateien [PASS].")
        content = PLANNING_FLAG.read_text()
        print(f"Inhalt des Flags:\n{content}")
        if str(test_md_file) not in content:
             print("[PASS] Trap 2, Test B: Unsere Datei ist aus dem Flag verschwunden. Der Mechanismus greift!")
        else:
             print("[FAIL] Trap 2, Test B: Datei steht immer noch auf der Liste!")
             sys.exit(1)

    # Cleanup Trap 2
    test_md_file.unlink()
    membrane.evaluate_all_and_sync_flags()

    print("\nAlle Traps erfolgreich durchlaufen!")

if __name__ == "__main__":
    main()
