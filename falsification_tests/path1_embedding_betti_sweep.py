"""
Pfad 1 — Falsifikations-Test der FTOE §3.4.2-Vorhersage.

FTOE-Behauptung (V5 §3.4.2): "Wenn Margin Loss > 0,049, kollabiert die Betti-Zahl-
Komplexität des Embedding-Raums abrupt ('Reasoning Collapse'). Lineares Absinken
würde die FTOE falsifizieren."

Dieser Test prüft die strukturelle (modell-unabhängige) Variante der These:
ist die Cosine-Distanz 0,049 eine kritische Schwelle für topologische Komplexität
(H_1-Persistence) in synthetisch generierten Cluster-Wolken im hoch-dimensionalen
Embedding-Raum?

Hypothesen:
  H_0 (Null):   H_1-Persistence degradiert linear/glatt mit zunehmender Cluster-
                Distanz. Kein Knick bei 0,049 -> FTOE FALSIFIZIERT.
  H_1 (FTOE):   H_1-Persistence zeigt einen abrupten Sprung zwischen 0,049 und
                0,051 -> FTOE-Vorhersage stützt.

Methodik:
  1. Generiere 2 Cluster im 384-dim Embedding-Raum (typische sentence-transformer-Dim).
  2. Cluster-Zentren so platziert, dass Cosine-Distanz exakt d ist.
  3. Punkte um Zentrum mit kontrolliertem Rauschen.
  4. Vietoris-Rips-Filtration -> Betti-Persistence-Diagramm via ripser.
  5. Maximale H_1-Persistence pro Distanz d -> Plot.

Author: Cursor-Agent, im Auftrag der V5.1-Falsifikation-Phase, 2026-04-28
"""

from __future__ import annotations
import json
import time
from pathlib import Path
import numpy as np
from ripser import ripser

RNG_SEED = 0x49     # Hex 0x49 = 73 (zufaellig: liegt nah an unserem 0,049-Anker)
EMB_DIM = 384       # all-MiniLM-L6-v2-Dim, also Standard-Sentence-Embedding
N_PER_CLUSTER = 80
N_REPS = 5          # Wiederholungen pro Distanz fuer Stat
INTRA_FACTOR = 0.40 # Verhaeltnis Intra-Cluster-Spread zu Inter-Distanz

DISTANCES = [
    0.020,   # weit darunter
    0.030,
    0.040,
    0.0480,
    0.0490,  # *** kritischer Punkt ***
    0.0500,
    0.0510,  # *** kritischer Punkt + epsilon ***
    0.0520,
    0.060,
    0.080,
    0.100,
    0.150,
    0.200,
    0.300,
]


def make_cluster_pair(d_target: float, rng: np.random.Generator) -> np.ndarray:
    """
    Generiert zwei normalisierte Cluster im EMB_DIM-Raum, deren Cluster-Zentren
    einen Cosine-Abstand von ~d_target haben. Punkte werden auf Einheitskugel projiziert.
    """
    # Erstes Zentrum zufaellig auf Einheitskugel
    c1 = rng.standard_normal(EMB_DIM)
    c1 /= np.linalg.norm(c1)

    # Zweites Zentrum: c2 = a*c1 + b*v, mit v orthogonal zu c1, ||c2||=1
    # cos(c1,c2) = a -> wir wollen 1 - cos = d_target => a = 1 - d_target
    a = 1.0 - d_target
    v = rng.standard_normal(EMB_DIM)
    v -= (v @ c1) * c1   # Gram-Schmidt
    v /= np.linalg.norm(v)
    b = float(np.sqrt(max(0.0, 1.0 - a * a)))
    c2 = a * c1 + b * v
    c2 /= np.linalg.norm(c2)  # Numerik-Hygiene

    sigma_intra = INTRA_FACTOR * d_target

    cluster_a = c1 + sigma_intra * rng.standard_normal((N_PER_CLUSTER, EMB_DIM))
    cluster_b = c2 + sigma_intra * rng.standard_normal((N_PER_CLUSTER, EMB_DIM))

    pts = np.vstack([cluster_a, cluster_b])
    pts /= np.linalg.norm(pts, axis=1, keepdims=True)
    return pts


def cosine_dmat(pts: np.ndarray) -> np.ndarray:
    """Cosine-Distanz-Matrix: 1 - <x,y> fuer normalisierte x,y."""
    cos_sim = pts @ pts.T
    cos_sim = np.clip(cos_sim, -1.0, 1.0)
    return 1.0 - cos_sim


def betti_metrics(pts: np.ndarray) -> dict:
    """
    Vietoris-Rips-Persistence ueber Cosine-Distanz-Matrix; gibt Schluesselgroessen
    der Betti-Persistence zurueck.
    """
    dmat = cosine_dmat(pts)
    res = ripser(dmat, distance_matrix=True, maxdim=1)
    h0 = res["dgms"][0]
    h1 = res["dgms"][1]

    finite_h0 = h0[np.isfinite(h0[:, 1])]
    h0_persistence = (finite_h0[:, 1] - finite_h0[:, 0]) if len(finite_h0) else np.array([])
    h1_persistence = (h1[:, 1] - h1[:, 0]) if len(h1) else np.array([])

    return {
        "n_h0": int(len(h0)),
        "n_h1": int(len(h1)),
        "h0_max_persist": float(h0_persistence.max()) if h0_persistence.size else 0.0,
        "h0_total_persist": float(h0_persistence.sum()) if h0_persistence.size else 0.0,
        "h1_max_persist": float(h1_persistence.max()) if h1_persistence.size else 0.0,
        "h1_total_persist": float(h1_persistence.sum()) if h1_persistence.size else 0.0,
        "h1_count": int(len(h1)),
    }


def run_sweep() -> list[dict]:
    rng_master = np.random.default_rng(RNG_SEED)
    results: list[dict] = []

    for d in DISTANCES:
        for rep in range(N_REPS):
            seed_rep = int(rng_master.integers(0, 2**31 - 1))
            rng_rep = np.random.default_rng(seed_rep)
            t0 = time.time()
            pts = make_cluster_pair(d, rng_rep)
            metrics = betti_metrics(pts)
            elapsed = time.time() - t0

            row = {
                "distance": d,
                "rep": rep,
                "seed": seed_rep,
                "elapsed_s": round(elapsed, 3),
                **metrics,
            }
            print(
                f"  d={d:7.4f}  rep={rep}  "
                f"H1_max={row['h1_max_persist']:.5f}  "
                f"H1_total={row['h1_total_persist']:.5f}  "
                f"#H1={row['h1_count']:4d}  "
                f"({elapsed:.2f}s)"
            )
            results.append(row)
    return results


def aggregate(results: list[dict]) -> list[dict]:
    """Aggregiert ueber Wiederholungen: mean + std je Distanz."""
    by_d: dict[float, list[dict]] = {}
    for r in results:
        by_d.setdefault(r["distance"], []).append(r)
    agg = []
    for d, rows in sorted(by_d.items()):
        h1_max = np.array([r["h1_max_persist"] for r in rows])
        h1_total = np.array([r["h1_total_persist"] for r in rows])
        h0_max = np.array([r["h0_max_persist"] for r in rows])
        agg.append({
            "distance": d,
            "n_reps": len(rows),
            "h1_max_mean": float(h1_max.mean()),
            "h1_max_std": float(h1_max.std()),
            "h1_total_mean": float(h1_total.mean()),
            "h1_total_std": float(h1_total.std()),
            "h0_max_mean": float(h0_max.mean()),
            "h0_max_std": float(h0_max.std()),
        })
    return agg


def discontinuity_score(agg: list[dict]) -> dict:
    """
    Sucht nach abruptem Sprung zwischen 0,049 und 0,051.
    Rueckgabe:
      - rel_jump: relativer Sprung der h1_max_mean
      - smoothness: durchschnittliche relative Schrittgroesse abseits des Knicks
      - z_jump: wie viele Std-Abweichungen der Knick im Vergleich zu Smoothness
    """
    sorted_agg = sorted(agg, key=lambda x: x["distance"])
    rel_steps = []
    jump_step = None

    for i in range(1, len(sorted_agg)):
        d_prev = sorted_agg[i - 1]["distance"]
        d_curr = sorted_agg[i]["distance"]
        h1_prev = sorted_agg[i - 1]["h1_max_mean"]
        h1_curr = sorted_agg[i]["h1_max_mean"]
        denom = abs(h1_prev) + 1e-12
        rel_step = abs(h1_curr - h1_prev) / denom

        is_critical_step = (
            abs(d_prev - 0.0490) < 1e-6 and abs(d_curr - 0.0500) < 1e-6
        ) or (
            abs(d_prev - 0.0500) < 1e-6 and abs(d_curr - 0.0510) < 1e-6
        ) or (
            abs(d_prev - 0.0490) < 1e-6 and abs(d_curr - 0.0510) < 1e-6
        )

        if is_critical_step:
            jump_step = max(jump_step or 0.0, rel_step)
        else:
            rel_steps.append(rel_step)

    smoothness_mean = float(np.mean(rel_steps)) if rel_steps else 0.0
    smoothness_std = float(np.std(rel_steps)) if rel_steps else 0.0
    z_jump = (
        (jump_step - smoothness_mean) / (smoothness_std + 1e-12)
        if jump_step is not None and rel_steps
        else None
    )

    return {
        "rel_jump_at_0049": jump_step,
        "smoothness_mean_rel_step": smoothness_mean,
        "smoothness_std_rel_step": smoothness_std,
        "z_jump": z_jump,
    }


def main() -> None:
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)

    print("=" * 78)
    print("PFAD 1 - FALSIFIKATIONS-TEST: Knick bei Cosine-Distanz 0,049 / 0,051?")
    print("=" * 78)
    print(f"  EMB_DIM        = {EMB_DIM}")
    print(f"  N_PER_CLUSTER  = {N_PER_CLUSTER}")
    print(f"  N_REPS         = {N_REPS}")
    print(f"  INTRA_FACTOR   = {INTRA_FACTOR}")
    print(f"  Distanzen      = {DISTANCES}")
    print(f"  RNG_SEED       = {RNG_SEED:#x}")
    print()
    print("Ergebnisse pro Distanz x Rep:")
    print("-" * 78)
    t_start = time.time()
    rows = run_sweep()
    t_total = time.time() - t_start

    agg = aggregate(rows)
    disc = discontinuity_score(agg)

    print()
    print("=" * 78)
    print("AGGREGATE - Mittelwerte ueber Wiederholungen je Distanz")
    print("=" * 78)
    print(f"{'distance':>10s}  {'h1_max_mean':>12s}  {'+-std':>10s}  {'h1_total_mean':>14s}  {'+-std':>10s}")
    print("-" * 78)
    for r in agg:
        print(
            f"{r['distance']:>10.4f}  "
            f"{r['h1_max_mean']:>12.5f}  "
            f"{r['h1_max_std']:>10.5f}  "
            f"{r['h1_total_mean']:>14.5f}  "
            f"{r['h1_total_std']:>10.5f}"
        )

    print()
    print("=" * 78)
    print("DISKONTINUITAETS-DETEKTOR (Knick zwischen 0,049 und 0,051?)")
    print("=" * 78)
    print(json.dumps(disc, indent=2))

    summary = {
        "params": {
            "emb_dim": EMB_DIM,
            "n_per_cluster": N_PER_CLUSTER,
            "n_reps": N_REPS,
            "intra_factor": INTRA_FACTOR,
            "distances": DISTANCES,
            "rng_seed": RNG_SEED,
        },
        "duration_s": round(t_total, 2),
        "rows": rows,
        "aggregate": agg,
        "discontinuity": disc,
    }
    out_path = out_dir / "path1_betti_sweep.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print()
    print(f"[OK] Dauer: {t_total:.2f}s, Output: {out_path}")


if __name__ == "__main__":
    main()
