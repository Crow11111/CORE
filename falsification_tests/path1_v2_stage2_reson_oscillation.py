"""
Pfad 1 v2 — STAGE 2: Oszillations-Test auf der RESON-Achse um 0,951.

Hypothese (User-getriggert): das alternierende Vorzeichen-Muster der Steigung
um 0,951 ist KEIN Rauschen, sondern Signatur der Z_4-Clock-Symmetrie
(FTOE-Operator Φ = e^{iπ/2} = i mit Φ^4 = 1).

Was Stage 1 zeigte (n=500):
  0,948 -> 0,949 : Steigung -0,49  (t=+1,54, p=0,12 — grenzwertig)
  0,949 -> 0,950 : Steigung -0,00  (t=+0,01, p=0,99 — null)
  0,950 -> 0,951 : Steigung +0,35  (t=-1,12, p=0,26 — grenzwertig)
  0,951 -> 0,952 : Steigung -0,25  (t=+0,74, p=0,46 — grenzwertig)

Wenn das real ist: bei n=10000 müsste |t| auf ~6,7 hochgehen (signifikant).
Wenn das Rauschen ist: |t| bleibt bei ~1,5.

Distanzen feiner gewählt um 0,951 zu erfassen, plus Kontrollpunkte oben/unten.
"""
from __future__ import annotations
import json
import time
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed
from ripser import ripser
from scipy import stats

RNG_MASTER = 0x95
EMB_DIM = 384
N_PER_CLUSTER = 50
N_REPS = 10000
INTRA_FACTOR = 0.40
N_JOBS = 8

DISTANCES = [0.940, 0.945, 0.947, 0.948, 0.949, 0.950, 0.951, 0.952, 0.953, 0.955, 0.957, 0.960]


def make_cluster_pair(d_target: float, rng: np.random.Generator) -> np.ndarray:
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


def runs_test(signs: list[int]) -> dict:
    """Wald-Wolfowitz-Runs-Test: Anzahl Vorzeichen-Wechsel signifikant?"""
    n_pos = sum(1 for s in signs if s > 0)
    n_neg = sum(1 for s in signs if s < 0)
    n = n_pos + n_neg
    if n < 2 or n_pos == 0 or n_neg == 0:
        return {"n_runs": None, "z": None, "p": None}
    n_runs = 1
    for i in range(1, len(signs)):
        if (signs[i] > 0) != (signs[i - 1] > 0):
            n_runs += 1
    expected = (2 * n_pos * n_neg / n) + 1
    var = (2 * n_pos * n_neg * (2 * n_pos * n_neg - n)) / (n**2 * (n - 1))
    z = (n_runs - expected) / np.sqrt(var) if var > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return {"n_runs": n_runs, "expected_runs": expected, "z": float(z), "p": float(p)}


def fourier_periodicity(deltas: list[float]) -> dict:
    """Sucht dominante Periode in der Steigungs-Reihe."""
    arr = np.array(deltas, dtype=float)
    if len(arr) < 4:
        return {"dominant_period": None}
    arr = arr - arr.mean()
    spec = np.abs(np.fft.rfft(arr))**2
    freqs = np.fft.rfftfreq(len(arr), d=1.0)
    if len(spec) < 2:
        return {"dominant_period": None}
    idx = int(np.argmax(spec[1:]) + 1)
    return {
        "spectrum_dc_removed": [float(s) for s in spec],
        "dominant_freq_index": idx,
        "dominant_period_steps": float(1.0 / freqs[idx]) if freqs[idx] > 0 else None,
        "spectral_concentration_at_dom": float(spec[idx] / (spec[1:].sum() + 1e-30)),
    }


def main() -> None:
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    print("=" * 78)
    print("PFAD 1 v2 STAGE 2 — RESON-Achse Oszillations-Test (Z_4-Clock-Hypothese)")
    print("=" * 78)
    print(f"  Distanzen     : {DISTANCES}")
    print(f"  N_REPS        : {N_REPS}  (= 20x Stage 1)")
    print(f"  N_JOBS        : {N_JOBS}")
    print(f"  Total samples : {len(DISTANCES) * N_REPS}")

    rng_top = np.random.default_rng(RNG_MASTER)
    seeds = [int(rng_top.integers(0, 2**31 - 1)) for _ in range(len(DISTANCES) * N_REPS)]
    work = []
    for i, d in enumerate(DISTANCES):
        for r in range(N_REPS):
            work.append((d, seeds[i * N_REPS + r]))

    t0 = time.time()
    print("  starte parallel ...")
    out = Parallel(n_jobs=N_JOBS, batch_size=128)(
        delayed(betti_one_sample)(d, s) for d, s in work
    )
    elapsed = time.time() - t0
    print(f"  fertig in {elapsed:.1f}s ({len(work)/elapsed:.0f} samples/s)")

    h1_max = np.array([o[0] for o in out]).reshape(len(DISTANCES), N_REPS)
    h1_total = np.array([o[1] for o in out]).reshape(len(DISTANCES), N_REPS)

    print()
    print("AGGREGATE (n=10000 pro Distanz)")
    print("-" * 78)
    print(f"{'distance':>10s} {'h1_max_mean':>12s} {'sem':>10s} {'h1_total_mean':>14s} {'sem':>10s}")
    agg = []
    for i, d in enumerate(DISTANCES):
        m = float(h1_max[i].mean())
        sem = float(h1_max[i].std(ddof=1) / np.sqrt(N_REPS))
        mt = float(h1_total[i].mean())
        semt = float(h1_total[i].std(ddof=1) / np.sqrt(N_REPS))
        agg.append({"distance": d, "h1_max_mean": m, "h1_max_sem": sem,
                    "h1_total_mean": mt, "h1_total_sem": semt})
        print(f"{d:>10.4f} {m:>12.6f} {sem:>10.6f} {mt:>14.6f} {semt:>10.6f}")

    print()
    print("WELCH-t-TEST je Distanz-Schritt (n=10000)")
    print("-" * 78)
    print(f"{'from':>8s} {'to':>8s} {'Δ':>+10s} {'Steigung':>11s} {'Welch-t':>10s} {'p':>10s} {'Vorz':>5s}")
    welch = []
    deltas = []
    signs = []
    for i in range(1, len(DISTANCES)):
        a = h1_max[i - 1]
        b = h1_max[i]
        delta = float(b.mean() - a.mean())
        dd = DISTANCES[i] - DISTANCES[i - 1]
        slope = delta / dd
        t_stat, p_val = stats.ttest_ind(a, b, equal_var=False)
        sign = int(np.sign(delta)) if abs(delta) > 1e-10 else 0
        welch.append({
            "from": DISTANCES[i - 1], "to": DISTANCES[i],
            "delta": delta, "slope": slope,
            "welch_t": float(t_stat), "welch_p": float(p_val),
            "sign": sign,
        })
        deltas.append(delta)
        signs.append(sign)
        print(f"{DISTANCES[i-1]:>8.4f} {DISTANCES[i]:>8.4f} {delta:>+10.6f} {slope:>+11.4f} {float(t_stat):>+10.2f} {float(p_val):>10.2e} {sign:>+5d}")

    runs = runs_test(signs)
    fft = fourier_periodicity(deltas)

    print()
    print("OSZILLATIONS-DIAGNOSE")
    print("-" * 78)
    print(f"  Vorzeichen-Sequenz : {signs}")
    if runs["n_runs"] is not None:
        print(f"  Runs-Test          : n_runs={runs['n_runs']}, expected={runs['expected_runs']:.2f}, z={runs['z']:.2f}, p={runs['p']:.4f}")
    else:
        print("  Runs-Test          : nicht anwendbar (alle Vorzeichen gleich)")
    if fft.get("dominant_period_steps") is not None:
        print(f"  FFT dominant period: {fft['dominant_period_steps']:.2f} Schritte (concentration={fft['spectral_concentration_at_dom']:.3f})")

    n_significant = sum(1 for w in welch if w["welch_p"] < 0.001)
    n_total = len(welch)
    print(f"  signif. Schritte (p<0.001) : {n_significant}/{n_total}")
    if n_significant >= 3:
        max_t = max(abs(w["welch_t"]) for w in welch)
        print(f"  -> SIGNAL DETEKTIERT: max|t|={max_t:.2f}, mind. {n_significant} Schritte mit p<1e-3")
    else:
        print("  -> kein robustes Signal: Stage-1-Wackeln ist Rauschen")

    summary = {
        "params": {
            "emb_dim": EMB_DIM, "n_per_cluster": N_PER_CLUSTER,
            "n_reps": N_REPS, "n_jobs": N_JOBS, "intra_factor": INTRA_FACTOR,
            "distances": DISTANCES, "rng_master": RNG_MASTER,
        },
        "elapsed_s": elapsed,
        "aggregate": agg,
        "welch_neighbors": welch,
        "oscillation": {
            "signs": signs,
            "runs_test": runs,
            "fft": fft,
            "n_significant_p1e-3": int(n_significant),
            "n_total_steps": int(n_total),
        },
    }
    out_path = out_dir / "path1_v2_stage2_reson.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\n[OK] {out_path}")


if __name__ == "__main__":
    main()
