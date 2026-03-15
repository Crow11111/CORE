import sys
import os
import time

# Fix encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../')))

from src.logic_core.crystal_grid_engine import CrystalGridEngine, BARYONIC_DELTA, RESONANCE_LOCK, SYMMETRY_BREAK_HIGH

print('=== HARDWARE AUDIT: CRYSTAL GRID ENGINE ===')

# Test 1: Verbot der 0.0 (Kältetod)
res_0 = CrystalGridEngine.apply_operator_query(0.0)
print(f'[1] Input 0.0 -> Snapped to: {res_0} (Erwartet: {BARYONIC_DELTA})')
if res_0 != BARYONIC_DELTA:
    print('FEHLER: 0.0 nicht korrekt abgefangen!')
    sys.exit(1)

# Test 2: Verbot der 1.0 (Singularität)
res_1 = CrystalGridEngine.apply_operator_query(1.0)
print(f'[2] Input 1.0 -> Snapped to: {res_1} (Erwartet: {RESONANCE_LOCK})')
if res_1 != RESONANCE_LOCK:
    print('FEHLER: 1.0 nicht korrekt abgefangen!')
    sys.exit(1)

# Test 3: Baryonic Delta Snapping
res_delta = CrystalGridEngine.apply_operator_query(0.048)
print(f'[3] Input 0.048 -> Snapped to: {res_delta} (Erwartet: {BARYONIC_DELTA})')
if res_delta != BARYONIC_DELTA:
    print('FEHLER: Delta Snapping defekt!')
    sys.exit(1)

# Test 4: Symmetrie Bruch (0.5)
res_sym = CrystalGridEngine.apply_operator_query(0.5)
print(f'[4] Input 0.5 -> Snapped to: {res_sym} (Erwartet: {SYMMETRY_BREAK_HIGH})')
if res_sym != SYMMETRY_BREAK_HIGH:
    print('FEHLER: Symmetrie-Bruch defekt!')
    sys.exit(1)

print('\n[+] AUDIT BESTANDEN. Die Konstanten und die physikalischen Grenzen sind hart im Code verankert. Kein Blabla.')
