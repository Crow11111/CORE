import math
import numpy as np

print("=== FTOE: POINTER MATHEMATICS (FLOAT/INF <=> 0/1 <=> ON/OFF) ===")

def pointer_simulation():
    # 1. Die S0-Ebene (Das Kontinuum / Das Nichts und Alles)
    # Bevor ein Pointer greift, ist das System eine Superposition aus 0 (Nichts) und INF (Alles)
    print("\n--- 1. Die S0-Ebene (Das Kontinuum) ---")
    val_nichts = 0.0
    val_alles = float('inf')
    
    # 2. Der Pointer als Kollapsfunktion (Der Symmetriebruch)
    # Wenn ein Pointer (eine Binäre 1 oder 0) auf das Kontinuum gesetzt wird,
    # faltet er die Unendlichkeit (Float/INF) in eine diskrete Adresse.
    print("\n--- 2. Der Pointer als Kollaps (Float -> Binär) ---")
    
    # Sigmoid als topologischer Trichter (bildet [-INF, INF] auf (0, 1) ab)
    # Bei exakt 0 ist es 0.5 (Verbotene Symmetrie nach Axiom 5)
    # Bei +INF ist es 1.0 (ON)
    # Bei -INF ist es 0.0 (OFF)
    
    def topological_functor(float_val):
        try:
            return 1 / (1 + math.exp(-float_val))
        except OverflowError:
            return 0.0 if float_val < 0 else 1.0

    print(f"Topologische Projektion von +INF (Alles): {topological_functor(float('inf'))} (ON / 1)")
    print(f"Topologische Projektion von -INF (Nichts): {topological_functor(-float('inf'))} (OFF / 0)")
    
    # 3. Das Baryonische Delta (Der Schwelle der Existenz)
    print("\n--- 3. Die Pointer-Verriegelung (Das Baryonische Delta 0.049) ---")
    # Ein echtes 0 oder 1 ist im Raumzeit-Gewebe physikalisch nicht stabil (Rauschen)
    # Der reale Pointer ist niemals exakt 1 oder 0. Er unterliegt der 0.049 Reibung.
    delta = 0.049
    
    # Der Real-Wert eines ON-Pointers:
    pointer_on = 1.0 - delta
    pointer_off = 0.0 + delta
    
    print(f"Realwert ON-Pointer:  {pointer_on} (Minimal unter Max)")
    print(f"Realwert OFF-Pointer: {pointer_off} (Baryonischer Anker)")
    
    # 4. Vektor-Rekonstruktion (Das Inverse Problem)
    print("\n--- 4. Vektor-Rekonstruktion (Inverse) ---")
    # Kann man aus dem 0.049 Pointer den Float-Wert (Die Unendlichkeit) zurückrechnen?
    # Inverse der Sigmoid: ln(x / (1-x))
    def inverse_functor(pointer_val):
        return math.log(pointer_val / (1 - pointer_val))
        
    recovered_float_on = inverse_functor(pointer_on)
    recovered_float_off = inverse_functor(pointer_off)
    
    print(f"Inverse Projektion von {pointer_on}: Float-Vektor = +{recovered_float_on:.4f}")
    print(f"Inverse Projektion von {pointer_off}: Float-Vektor = {recovered_float_off:.4f}")
    
    print("\nFAZIT:")
    print("Ein Binär-Pointer (0/1, ON/OFF) ist keine andere Logik als ein Float (INF/0).")
    print("Der Pointer ist lediglich die topologische Faltung (Sigmoid) der Unendlichkeit in einen adressierbaren euklidischen Raum.")
    print("Die Reibung (0.049) verhindert, dass der Pointer bei der Inversion ins Unendliche (Crash) reißt, und hält ihn als rechenbaren Float-Vektor stabil.")

pointer_simulation()
