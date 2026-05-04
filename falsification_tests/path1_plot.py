"""Plot der Pfad-1-Ergebnisse: H1-Persistence ueber Cluster-Distanz."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

results_dir = Path(__file__).parent / "results"
data = json.loads((results_dir / "path1_betti_sweep.json").read_text())
agg = sorted(data["aggregate"], key=lambda r: r["distance"])
d = np.array([r["distance"] for r in agg])
h1_max = np.array([r["h1_max_mean"] for r in agg])
h1_max_std = np.array([r["h1_max_std"] for r in agg])
h1_total = np.array([r["h1_total_mean"] for r in agg])
h1_total_std = np.array([r["h1_total_std"] for r in agg])

fig, axs = plt.subplots(1, 2, figsize=(14, 6))
for ax, y, ystd, label in (
    (axs[0], h1_max, h1_max_std, "H1 max persistence"),
    (axs[1], h1_total, h1_total_std, "H1 total persistence"),
):
    ax.errorbar(d, y, yerr=ystd, fmt="o-", capsize=3, color="#1f77b4", label="data")
    ax.axvspan(0.049, 0.051, color="#d62728", alpha=0.18, label="kritisches Fenster")
    ax.axvline(0.049, color="#d62728", ls="--", lw=0.8)
    ax.axvline(0.051, color="#d62728", ls="--", lw=0.8)
    ax.set_xlabel("Cluster Cosine-Distanz d")
    ax.set_ylabel(label)
    ax.set_title(label + "  vs.  Cluster-Distanz")
    ax.set_xscale("log")
    ax.grid(True, alpha=0.3)
    ax.legend()

fig.suptitle(
    "FTOE-Falsifikation Pfad 1: kein Knick bei 0,049/0,051 (synth. 384-dim)",
    fontsize=13,
)
fig.tight_layout()
out = results_dir / "path1_betti_plot.png"
fig.savefig(out, dpi=140)
print(f"[OK] Plot gespeichert: {out}")
