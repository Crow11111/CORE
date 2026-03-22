#!/usr/bin/env python3
"""
Wertet JSONL aus benchmark_whitepaper_anchors.py aus (Struktur + Plausibilität).

Exit 0: alle Paare konsistent.
Exit 1: fehlende Paare, falsche Outcomes oder Iterations-Mismatch.

Optional: --max-ratio für Wall-Zeit (ohne/mit), Default weit (Mikrosekunden-Rauschen).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCHEMA = "omega.benchmark.whitepaper_anchors.v1"


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", type=Path, help="Pfad zur .jsonl")
    ap.add_argument(
        "--max-ratio",
        type=float,
        default=25.0,
        help="Max. erlaubt schleifen_wall_ms(ohne)/schleifen_wall_ms(mit) (Rauschen bei µs)",
    )
    args = ap.parse_args()

    rows = load_rows(args.jsonl)
    by_pair: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if r.get("schema") != SCHEMA:
            print(f"[FAIL] unbekanntes schema: {r.get('schema')}", file=sys.stderr)
            return 1
        by_pair[r["pair_id"]].append(r)

    fails = 0
    for pair_id, pr in sorted(by_pair.items()):
        if len(pr) != 2:
            print(f"[FAIL] pair_id={pair_id}: erwartet 2 Zeilen, hat {len(pr)}", file=sys.stderr)
            fails += 1
            continue
        phases = {x["phase"] for x in pr}
        if phases != {"mit_kardan", "ohne_kardan_paired"}:
            print(f"[FAIL] pair_id={pair_id}: Phasen {phases}", file=sys.stderr)
            fails += 1
            continue
        mit = next(x for x in pr if x["phase"] == "mit_kardan")
        ohne = next(x for x in pr if x["phase"] == "ohne_kardan_paired")
        if mit["outcome"] != "converged_complex":
            print(f"[FAIL] {pair_id} mit outcome {mit['outcome']}", file=sys.stderr)
            fails += 1
        if ohne["outcome"] != "paired_fixed_ticks":
            print(f"[FAIL] {pair_id} ohne outcome {ohne['outcome']}", file=sys.stderr)
            fails += 1
        if mit["iterations"] != ohne["iterations"]:
            print(
                f"[FAIL] {pair_id} iterations {mit['iterations']} != {ohne['iterations']}",
                file=sys.stderr,
            )
            fails += 1
        rw = ohne["schleifen_wall_ms"] / max(mit["schleifen_wall_ms"], 1e-12)
        if rw > args.max_ratio or rw < 1.0 / args.max_ratio:
            print(
                f"[FAIL] {pair_id} Wall-Ratio ohne/mit={rw} ausserhalb "
                f"[1/{args.max_ratio}, {args.max_ratio}]",
                file=sys.stderr,
            )
            fails += 1

    if fails:
        print(f"[EVAL_FAIL] {fails} Verstoss(e)", file=sys.stderr)
        return 1
    print(f"[EVAL_PASS] {len(by_pair)} Paar(e) in {args.jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
