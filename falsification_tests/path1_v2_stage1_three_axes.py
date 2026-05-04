"""
Pfad 1 v2 — STAGE 1: zweistufiger Falsifikations-Test mit drei Achsen.

Korrigiert die folgenden Punkte des v1-Tests:
  1. Statistische Power: n_reps von 5 auf 500 (100x mehr Stichproben).
  2. Drei Achsen statt einer:
       - Außenwand-Achse um 0,049     (klassische Lesart, V5 §3.4.2)
       - Symmetrie-Achse um 0,5        (Symmetrie-Tod, "Innenwand")
       - Resonanz-Achse um 0,951        (= 1 - 0,049, Resonanz-Lock)
  3. Detektor-Statistik: Welch-t-Test zwischen benachbarten Distanzen,
     keine reine Punktschätzung.
  4. Parallelisiert via joblib (n_jobs=8 von 12 Cores).

Wenn an einer der drei Achsen ein abrupter Sprung mit Welch-t > 5σ erscheint,
geht der nächste Schritt (STAGE 2) auf n_reps=100.000 für diese Achse.
"""

from __future__ import annotations
import json
import time
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed
from ripser import ripser
from scipy import stats

RNG_MASTER = 0x49
EMB_DIM = 384
N_PER_CLUSTER = 50
N_REPS = 500
INTRA_FACTOR = 0.40
N_JOBS = 8

AXIS_OUTER = [0.030, 0.040, 0.045, 0.048, 0.049, 0.050, 0.051, 0.052, 0.055, 0.060, 0.080, 0.100]
AXIS_INNER = [0.30,  0.40,  0.45,  0.48,  0.49,  0.50,  0.51,  0.52,  0.55,  0.60,  0.70,  0.90]
AXIS_RESON = [0.90,  0.92,  0.94,  0.948, 0.949, 0.950, 0.951, 0.952, 0.955, 0.96,  0.98,  0.99]


def make_cluster_pair(d_target: float, rng: np.random.Generator) -> np.ndarray:
    """Zwei Cluster auf der Einheitskugel mit Zentren-Cosine-Distanz ~ d_target."""
    c1 = rng.standard_normal(EMB_DIM)
    c1 /= np.linalg.norm(c1)
    a = 1.0 - d_target
    v = rng.standard_normal(EMB_DIM)
    v -= (v @ c1) * c1
    v /= np.linalg.norm(v)
    b = float(np.sqrt(max(0.0, 1.0 - a * a)))
    c2 = a * c1 + b * v
    c2 /= np.linalg.norm(c2)

    sigma_intra = INTRA_FACTOR * d_target
    pa = c1 + sigma_intra * rng.standard_normal((N_PER_CLUSTER, EMB_DIM))
    pb = c2 + sigma_intra * rng.standard_normal((N_PER_CLUSTER, EMB_DIM))
    pts = np.vstack([pa, pb])
    pts /= np.linalg.norm(pts, axis=1, keepdims=True)
    return pts


def cosine_dmat(pts: np.ndarray) -> np.ndarray:
    s = pts @ pts.T
    s = np.clip(s, -1.0, 1.0)
    return 1.0 - s


def betti_one_sample(d_target: float, seed: int) -> tuple[float, float, int]:
    rng = np.random.default_rng(seed)
    pts = make_cluster_pair(d_target, rng)
    dmat = cosine_dmat(pts)
    res = ripser(dmat, distance_matrix=True, maxdim=1)
    h1 = res["dgms"][1]
    if len(h1) == 0:
        return 0.0, 0.0, 0
    pers = h1[:, 1] - h1[:, 0]
    return float(pers.max()), float(pers.sum()), int(len(h1))


def run_axis(name: str, distances: list[float], n_reps: int) -> dict:
    print(f"\n=== Achse: {name}  ({len(distances)} Distanzen × {n_reps} Reps = {len(distances) * n_reps} Samples) ===")
    rng_top = np.random.default_rng(RNG_MASTER ^ hash(name) & 0xFFFFFFFF)
    seeds = [int(rng_top.integers(0, 2**31 - 1)) for _ in range(len(distances) * n_reps)]

    t0 = time.time()
    work = []
    for i, d in enumerate(distances):
        for r in range(n_reps):
            seed = seeds[i * n_reps + r]
            work.append((d, seed))

    print(f"  start: n_jobs={N_JOBS}  (work={len(work)} jobs)")
    out = Parallel(n_jobs=N_JOBS, batch_size=64, verbose=2)(
        delayed(betti_one_sample)(d, s) for d, s in work
    )
    elapsed = time.time() - t0
    print(f"  Achse {name} fertig in {elapsed:.1f}s")

    h1_max = np.array([o[0] for o in out]).reshape(len(distances), n_reps)
    h1_total = np.array([o[1] for o in out]).reshape(len(distances), n_reps)
    h1_count = np.array([o[2] for o in out]).reshape(len(distances), n_reps)

    agg = []
    for i, d in enumerate(distances):
        agg.append({
            "distance": d,
            "h1_max_mean": float(h1_max[i].mean()),
            "h1_max_std": float(h1_max[i].std(ddof=1)),
            "h1_total_mean": float(h1_total[i].mean()),
            "h1_total_std": float(h1_total[i].std(ddof=1)),
            "h1_count_mean": float(h1_count[i].mean()),
        })

    welch = []
    for i in range(1, len(distances)):
        a = h1_max[i - 1]
        b = h1_max[i]
        t_stat, p_val = stats.ttest_ind(a, b, equal_var=False)
        delta = float(b.mean() - a.mean())
        welch.append({
            "from": distances[i - 1],
            "to": distances[i],
            "delta_h1_max": delta,
            "welch_t": float(t_stat),
            "welch_p": float(p_val),
            "rel_step_pct": 100.0 * delta / (a.mean() + 1e-15),
        })

    return {
        "axis": name,
        "n_reps": n_reps,
        "distances": distances,
        "elapsed_s": elapsed,
        "aggregate": agg,
        "welch_neighbors": welch,
    }


def signal_diagnosis(results: list[dict]) -> dict:
    """Findet je Achse die maximal-signifikante Diskontinuität."""
    diag = {}
    for r in results:
        max_t = max(abs(w["welch_t"]) for w in r["welch_neighbors"])
        biggest = max(r["welch_neighbors"], key=lambda w: abs(w["welch_t"]))
        diag[r["axis"]] = {
            "max_abs_welch_t": float(max_t),
            "biggest_step_from": biggest["from"],
            "biggest_step_to": biggest["to"],
            "biggest_delta_h1_max": biggest["delta_h1_max"],
            "biggest_p": biggest["welch_p"],
        }
    return diag


def main() -> None:
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    print("PFAD 1 v2 STAGE 1 — drei Achsen, n_reps=500, n_jobs=8")
    print(f"  EMB_DIM = {EMB_DIM}, N_PER_CLUSTER = {N_PER_CLUSTER}, INTRA_FACTOR = {INTRA_FACTOR}")

    t0 = time.time()
    results = [
        run_axis("OUTER_around_0049", AXIS_OUTER, N_REPS),
        run_axis("INNER_around_0500", AXIS_INNER, N_REPS),
        run_axis("RESON_around_0951", AXIS_RESON, N_REPS),
    ]
    total_time = time.time() - t0

    diag = signal_diagnosis(results)

    print("\n" + "=" * 78)
    print("STAGE-1-DIAGNOSE: Welch-t-Statistik max-Sprung pro Achse")
    print("=" * 78)
    for axis, d in diag.items():
        flag = "STARK" if d["max_abs_welch_t"] > 5 else ("MITTEL" if d["max_abs_welch_t"] > 3 else "schwach/Rauschen")
        print(f"  {axis:<25}  max|t|={d['max_abs_welch_t']:>6.2f}  zw. {d['biggest_step_from']:.4f}→{d['biggest_step_to']:.4f}  Δ={d['biggest_delta_h1_max']:+.5f}  p={d['biggest_p']:.2e}   [{flag}]")

    print(f"\n  Total: {total_time:.1f}s")
    summary = {
        "params": {
            "emb_dim": EMB_DIM,
            "n_per_cluster": N_PER_CLUSTER,
            "n_reps": N_REPS,
            "intra_factor": INTRA_FACTOR,
            "n_jobs": N_JOBS,
        },
        "total_time_s": total_time,
        "results": results,
        "diagnosis": diag,
    }
    out_path = out_dir / "path1_v2_stage1.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\n[OK] {out_path}")


if __name__ == "__main__":
    main()
