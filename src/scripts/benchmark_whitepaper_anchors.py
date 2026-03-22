#!/usr/bin/env python3
"""
Paar-Benchmark für Whitepaper-/Kardan-Behauptungen (mit vs. ohne Kontrolle).

- „mit“: Kardan aktiv → Konvergenz über komplexen Sprung (wie Produktions-Demo omega_core.py).
- „ohne“: gleiche Iterationszahl, Kardan aus → nur reeller Symbiose-Pfad; gleiche CPU-Arbeit pro Tick.

Ausgabe: JSON Lines (eine Zeile pro Lauf) unter logs/benchmarks/ — auswertbar ohne stdout-Poesie.
Messgrößen: schleifen_wall_ms, process_cpu_ms (reelle Prozessorzeit), optional RAPL-Paketenergie (Joule),
  wenn /sys/class/powercap lesbar ist.

Kein LLM → keine Token-Metrik hier (explizit 0 / nicht anwendbar).
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
import uuid
from pathlib import Path

# Repo-Root (…/OMEGA_CORE)
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import omega_core as oc  # noqa: E402


def _read_rapl_joules() -> float | None:
    """Summe intel-rapl *energy_uj* in Joule, falls lesbar."""
    base = Path("/sys/class/powercap")
    if not base.is_dir():
        return None
    total_uj = 0
    found = False
    for energy_file in base.glob("intel-rapl:*"):
        p = energy_file / "energy_uj"
        if not p.is_file():
            continue
        try:
            total_uj += int(p.read_text(encoding="ascii").strip())
            found = True
        except (OSError, ValueError):
            continue
    return (total_uj / 1e6) if found else None


def _envelope(
    *,
    pair_id: str,
    phase: str,
    harness: dict,
    rapl_j_start: float | None,
    rapl_j_end: float | None,
    repeats_index: int,
) -> dict:
    row = {
        "schema": "omega.benchmark.whitepaper_anchors.v1",
        "pair_id": pair_id,
        "phase": phase,
        "repeats_index": repeats_index,
        "hostname": socket.gethostname(),
        "ts_unix": time.time(),
        "tokens_llm": None,
        "tokens_note": "kein LLM in diesem Harness",
        "rapl_joules_pkg_approx": None,
        "rapl_note": None,
        **harness,
    }
    if rapl_j_start is not None and rapl_j_end is not None:
        row["rapl_joules_pkg_approx"] = max(0.0, rapl_j_end - rapl_j_start)
        row["rapl_note"] = "Summe intel-rapl:* energy_uj Delta; Granularität plattformabhängig"
    else:
        row["rapl_note"] = "RAPL nicht lesbar (Rechte/Hardware) — nur Wall/CPU-Metriken verbindlich"
    return row


def run_pair(
    *,
    initial_s_float: float,
    p_int_start: int,
    max_ticks_safety: int,
) -> tuple[dict, dict]:
    pair_id = str(uuid.uuid4())
    uid_mit = str(uuid.uuid4())

    e0 = _read_rapl_joules()
    t_wall0 = time.perf_counter()
    mit = oc.run_autopoiesis_harness(
        enable_kardan=True,
        initial_s_float=initial_s_float,
        p_int_start=p_int_start,
        run_uuid=uid_mit,
        max_ticks_safety=max_ticks_safety,
        fixed_tick_limit=None,
    )
    t_wall1 = time.perf_counter()
    e1 = _read_rapl_joules()

    if mit["outcome"] != "converged_complex":
        raise RuntimeError(f"mit: erwartet converged_complex, ist {mit['outcome']}")

    n_iter = mit["iterations"]
    uid_ohne = str(uuid.uuid4())

    e2 = _read_rapl_joules()
    ohne = oc.run_autopoiesis_harness(
        enable_kardan=False,
        initial_s_float=initial_s_float,
        p_int_start=p_int_start,
        run_uuid=uid_ohne,
        max_ticks_safety=max_ticks_safety,
        fixed_tick_limit=n_iter,
    )
    e3 = _read_rapl_joules()

    if ohne["outcome"] != "paired_fixed_ticks":
        raise RuntimeError(f"ohne: erwartet paired_fixed_ticks, ist {ohne['outcome']}")
    if ohne["iterations"] != n_iter:
        raise RuntimeError(
            f"ohne: Iterationszahl {ohne['iterations']} != mit {n_iter}"
        )

    row_mit = _envelope(
        pair_id=pair_id,
        phase="mit_kardan",
        harness=mit,
        rapl_j_start=e0,
        rapl_j_end=e1,
        repeats_index=0,
    )
    row_mit["subprocess_wall_ms"] = (t_wall1 - t_wall0) * 1000.0

    row_ohne = _envelope(
        pair_id=pair_id,
        phase="ohne_kardan_paired",
        harness=ohne,
        rapl_j_start=e2,
        rapl_j_end=e3,
        repeats_index=0,
    )
    return row_mit, row_ohne


def main() -> int:
    ap = argparse.ArgumentParser(description="Whitepaper-Anker: mit/ohne Paar-Benchmark")
    ap.add_argument("--repeats", type=int, default=1, help="Anzahl unabhängiger Paare")
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "logs" / "benchmarks" / "whitepaper_anchors.jsonl",
        help="JSONL-Zieldatei",
    )
    ap.add_argument("--initial-s", type=float, default=0.51)
    ap.add_argument("--p-int-start", type=int, default=1)
    ap.add_argument("--max-ticks-safety", type=int, default=1_000_000)
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    for r in range(args.repeats):
        row_mit, row_ohne = run_pair(
            initial_s_float=args.initial_s,
            p_int_start=args.p_int_start,
            max_ticks_safety=args.max_ticks_safety,
        )
        row_mit["repeats_index"] = r
        row_ohne["repeats_index"] = r
        all_rows.extend([row_mit, row_ohne])

    with args.out.open("a", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Auswertung letztes Paar (repeats=1 typisch)
    last_mit = all_rows[-2]
    last_ohne = all_rows[-1]
    ratio_wall = last_ohne["schleifen_wall_ms"] / max(last_mit["schleifen_wall_ms"], 1e-9)
    ratio_cpu = last_ohne["process_cpu_ms"] / max(last_mit["process_cpu_ms"], 1e-9)

    summary = {
        "pairs_written": args.repeats,
        "log_path": str(args.out),
        "last_pair_id": last_mit["pair_id"],
        "mit_iterations": last_mit["iterations"],
        "ratio_ohne_per_mit_wall": ratio_wall,
        "ratio_ohne_per_mit_cpu": ratio_cpu,
        "interpretation": (
            "Ohne-Kontrolle: gleiche Schleifeniterationen wie mit, aber durchgehend reeller Pfad; "
            "mit endet mit komplexem Kardan-Tick. Wall/CPU-Verhältnis wird nur geloggt "
            "(kein Identitätsgesetz bei µs-Messung)."
        ),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("[BENCHMARK_PASS] Paar mit/ohne geschrieben; siehe log_path")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc), "type": type(exc).__name__}, ensure_ascii=False))
        print("[BENCHMARK_FAIL]", exc, file=sys.stderr)
        raise SystemExit(1)
