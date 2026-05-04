"""
Pfad 1b - Falsifikations-Test mit ECHTEN Embeddings via Ollama.

Nutzt qwen2.5:7b oder gemma2:2b als Embedding-Modell ueber Ollamas /api/embeddings.
Wir konstruieren Saetze mit kontrollierter semantischer Aehnlichkeit, messen ihre
Cosinus-Distanz und pruefen, ob 0,049/0,051 in dem realen Embedding-Raum eine
strukturelle Sonderrolle hat.
"""
from __future__ import annotations
import json
import time
from pathlib import Path

import numpy as np
import requests
from ripser import ripser

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text:latest"

THEMES = {
    "tech": [
        "Quantum computers may break RSA encryption.",
        "GPUs accelerate matrix multiplications massively.",
        "Transformers use attention to model long sequences.",
        "Convolutional networks excel at image classification.",
        "Backpropagation computes gradients via chain rule.",
        "Tensor cores boost mixed-precision throughput.",
        "Floating-point arithmetic introduces rounding error.",
        "Embeddings represent meaning in vector space.",
        "Self-attention scales quadratically with context length.",
        "Reinforcement learning balances exploration and exploitation.",
        "Diffusion models denoise data step by step.",
        "Sparsity reduces inference cost without losing quality.",
        "Mixed precision training stabilises gradients.",
        "Distillation compresses large models into small ones.",
        "Speculative decoding accelerates LLM inference.",
        "RoPE rotary embeddings encode relative positions.",
        "FlashAttention reduces memory I/O during training.",
        "Quantization shrinks model footprints aggressively.",
        "Vector databases index high-dimensional embeddings.",
        "Latent diffusion compresses image space efficiently.",
    ],
    "biology": [
        "Photosynthesis converts sunlight into chemical energy.",
        "DNA encodes genetic information in four bases.",
        "Enzymes catalyse biochemical reactions.",
        "Mitochondria generate ATP via oxidative phosphorylation.",
        "Neurons fire action potentials to transmit signals.",
        "Apoptosis is programmed cell death.",
        "CRISPR enables precise gene editing.",
        "Ribosomes translate mRNA into proteins.",
        "Stem cells differentiate into specialised tissues.",
        "Antibodies recognise foreign antigens.",
        "Phagocytes engulf invading microbes.",
        "Synaptic plasticity underlies learning.",
        "Telomeres shorten with each cell division.",
        "Chloroplasts store starch as energy reserve.",
        "Hormones coordinate distant organs in the body.",
        "Mitosis duplicates chromosomes equally.",
        "Receptors bind ligands with high specificity.",
        "Microbes outnumber human cells in our gut.",
        "Endorphins modulate pain perception.",
        "Mitochondrial DNA traces maternal lineage.",
    ],
}


def get_embedding(text: str) -> np.ndarray:
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": text},
        timeout=60,
    )
    r.raise_for_status()
    e = np.array(r.json()["embedding"], dtype=np.float64)
    e /= np.linalg.norm(e)
    return e


def cosine_dmat(pts: np.ndarray) -> np.ndarray:
    s = pts @ pts.T
    s = np.clip(s, -1.0, 1.0)
    return 1.0 - s


def main() -> None:
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    print(f"[INFO] Modell: {MODEL}")

    embeddings: dict[str, np.ndarray] = {}
    print("[INFO] Hole Embeddings ueber Ollama ...")
    t0 = time.time()
    for theme, sentences in THEMES.items():
        arr = []
        for s in sentences:
            arr.append(get_embedding(s))
        embeddings[theme] = np.vstack(arr)
        print(f"  {theme:<10s}  shape={embeddings[theme].shape}  dim={embeddings[theme].shape[1]}")
    print(f"[INFO] {time.time() - t0:.1f}s fuer Embedding-Sammlung")

    # Fuse alle Embeddings, Cosine-Distanz-Matrix berechnen, Verteilung anschauen
    all_pts = np.vstack(list(embeddings.values()))
    dmat = cosine_dmat(all_pts)
    iu = np.triu_indices_from(dmat, k=1)
    distances = dmat[iu]
    print()
    print("[INFO] Verteilung paarweiser Cosine-Distanzen:")
    print(f"  Anzahl  = {len(distances)}")
    print(f"  Min     = {distances.min():.5f}")
    print(f"  q05     = {np.quantile(distances, 0.05):.5f}")
    print(f"  Median  = {np.median(distances):.5f}")
    print(f"  q95     = {np.quantile(distances, 0.95):.5f}")
    print(f"  Max     = {distances.max():.5f}")

    # Vietoris-Rips Filtration ueber den GESAMTEN echten Embedding-Raum
    res = ripser(dmat, distance_matrix=True, maxdim=1)
    h1 = res["dgms"][1]
    print()
    print(f"[INFO] H1-Persistence (Anzahl Loops): {len(h1)}")

    # Counts pro Filtrations-Bin
    bins = [0, 0.04, 0.045, 0.048, 0.049, 0.050, 0.051, 0.052, 0.06, 0.10, 0.20, 0.50]
    bin_counts = []
    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i + 1]
        c = int(((h1[:, 0] >= lo) & (h1[:, 0] < hi)).sum())
        bin_counts.append({"birth_lo": lo, "birth_hi": hi, "n_h1_births": c})
        print(f"  H1-Geburten in [{lo:.4f}, {hi:.4f})  =  {c}")

    # Persistence pro Loop
    pers = h1[:, 1] - h1[:, 0]
    pers_at_critical = pers[(h1[:, 0] >= 0.045) & (h1[:, 0] <= 0.055)]
    pers_around_critical = pers[(h1[:, 0] >= 0.040) & (h1[:, 0] <= 0.045)]

    print()
    print(f"[INFO] H1-Persistence BIRTH bei [0.045, 0.055]: n={len(pers_at_critical)}, "
          f"mean={pers_at_critical.mean() if len(pers_at_critical) else 0:.5f}, "
          f"max={pers_at_critical.max() if len(pers_at_critical) else 0:.5f}")
    print(f"[INFO] H1-Persistence BIRTH bei [0.040, 0.045]: n={len(pers_around_critical)}, "
          f"mean={pers_around_critical.mean() if len(pers_around_critical) else 0:.5f}, "
          f"max={pers_around_critical.max() if len(pers_around_critical) else 0:.5f}")

    summary = {
        "model": MODEL,
        "n_sentences": int(all_pts.shape[0]),
        "embedding_dim": int(all_pts.shape[1]),
        "distance_distribution": {
            "min": float(distances.min()),
            "q05": float(np.quantile(distances, 0.05)),
            "median": float(np.median(distances)),
            "q95": float(np.quantile(distances, 0.95)),
            "max": float(distances.max()),
        },
        "h1_total_loops": int(len(h1)),
        "h1_births_per_bin": bin_counts,
    }
    out_path = out_dir / "path1b_real_embeddings.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"[OK] gespeichert: {out_path}")


if __name__ == "__main__":
    main()
