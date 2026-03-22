#!/usr/bin/env python3
"""
Rat der Titanen — Runde 2: ausformuliertes Whitepaper → reviews_2.

Gleiches Setting wie run_omega_science_council.py:
- Ollama: OLLAMA_LOCAL_HOST (default http://127.0.0.1:11434)
- Modell: OMEGA_COUNCIL_MODEL (default qwen2.5:14b)
- temperature 0.2, Streaming

Vom Repo-Root:
  python3 src/scripts/run_omega_science_council_r2.py
  python3 src/scripts/run_omega_science_council_r2.py --force
"""
import argparse
import asyncio
import importlib.util
import os
from pathlib import Path

R2_PAPER = "docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_Informationsgrafitation ausformuliert.md"
R2_OUT = "docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2"
R2_TITLE = (
    "OMEGA_CORE WHITE PAPER (ausformuliert): INFORMATIONSGRAVITATION, MRI, 5D-TORUS — Runde 2"
)


def _load_council_module():
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "_omega_science_council", here / "run_omega_science_council.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    ap = argparse.ArgumentParser(description="Science Council R2 → WHITEPAPER/reviews_2 (Ollama)")
    ap.add_argument("--force", action="store_true", help="Vorhandene Gutachten überschreiben")
    args = ap.parse_args()

    council = _load_council_module()

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(
        council.run_council_review(
            white_paper_path=R2_PAPER,
            reviews_dir=R2_OUT,
            paper_title=R2_TITLE,
            force=args.force,
        )
    )


if __name__ == "__main__":
    main()
