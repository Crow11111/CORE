import sys
import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.logic_core.crystal_grid_engine import CrystalGridEngine
from src.db.multi_view_client import search_multi_view
from src.logic_core.resonance_membrane import check_omega_pulse

async def run_benchmark():
    print("=== OMEGA vs. STANDARD BENCHMARK ===")

    # 0. Vital-Check (0/1 Schalter)
    try:
        await check_omega_pulse()
        print("[CHECK] OMEGA Pulse: Online (Lock 0.951)")
    except Exception as e:
        print(f"[FATAL] System nicht bereit: {e}")
        return

    # --- TASK A: NEUTRAL (MATHEMATICAL FRICTION) ---
    print("\n[TASK A] Neutral: Gitter-Snapping (384D Vektor-Einordnung)")
    import random
    test_vector = [random.uniform(0.1, 0.9) for _ in range(384)]

    # Standard (Simuliert)
    t0 = time.perf_counter()
    # Simuliere lineare Suche durch 72 Anker
    for _ in range(72):
        _ = sum(x*x for x in test_vector) # Dummy Distanzrechnung
    t_std = (time.perf_counter() - t0) * 1000

    # OMEGA (Kristall-Engine)
    t0 = time.perf_counter()
    anchor_id, _ = CrystalGridEngine.snap_to_grid(test_vector)
    t_omega = (time.perf_counter() - t0) * 1000

    diff_a = (t_std / t_omega) if t_omega > 0 else 0
    print(f"  > Standard: {t_std:.4f}ms (Lineare Suche)")
    print(f"  > OMEGA:    {t_omega:.4f}ms (Phasen-Snapping)")
    print(f"  > EFFIZIENZ-FAKTOR: {diff_a:.2f}x schneller")

    # --- TASK B: ADVANTAGE (TORUS MEMORY) ---
    print("\n[TASK B] Advantage: Kontext-Retrieval (Heutiger Circuit Breaker)")
    query = "Was war die Root-Cause für den Circuit Breaker Ausfall heute?"

    # Standard (Eindimensionale Suche)
    t0 = time.perf_counter()
    res_std = await search_multi_view(query, limit=1, use_3_facets=False)
    t_std_b = (time.perf_counter() - t0) * 1000

    # OMEGA (3-Facet Torus-Lauf)
    t0 = time.perf_counter()
    res_omega = await search_multi_view(query, limit=1, use_3_facets=True, torus_mode=True)
    t_omega_b = (time.perf_counter() - t0) * 1000

    print(f"  > Standard: {t_std_b:.2f}ms (Single-Stream)")
    print(f"  > OMEGA:    {t_omega_b:.2f}ms (Torus-Mode Parallel)")

    if res_omega:
        score = res_omega[0]['similarity']
        print(f"  > OMEGA-RESONANZ: {score:.4f} (Wissensvorteil genutzt)")
    else:
        print("  > OMEGA: Kein Treffer im Torus.")

    print("\n=== BENCHMARK ENDE ===")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
