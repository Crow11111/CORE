import math

# Suche nach "Zero Friction Anchors" (Kongruenz von Float-Kurven und Int-Gitter)
# Wir scannen Radien im 144-Orbit nach Punkten, an denen der euklidische Float-Umfang
# fast perfekt auf einen Int-Wert snappt (Fehler < 1e-4), oder perfekte Ratios bilden.

print("--- OMEGA FTOE: ZERO FRICTION ANCHOR SEARCH ---")
print("Suche nach Radien r (1 bis 144), bei denen der euklidische Umfang")
print("ohne nennenswertes Snapping auf das Int-Gitter passt.\n")

for r in range(1, 145):
    d = 2 * r
    float_circumference = d * math.pi
    int_snap = round(float_circumference)
    friction = abs(float_circumference - int_snap)
    
    # Toleranz für "Zero Friction" (sehr nahe an Kongruenz)
    if friction < 0.01:
        print(f"Radius {r} (d={d}): Float-Umfang = {float_circumference:.5f} -> Int-Snap = {int_snap}")
        print(f"  -> Reibung (Snapping-Delta): {friction:.6f}")
        print("-" * 50)
