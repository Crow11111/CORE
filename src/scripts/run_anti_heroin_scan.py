#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti-Heroin-Scan über alle src/**/*.py (Validator ausgenommen).

Eintrittspunkt für systemd auf dem VPS, CI und run_vollkreis_abnahme (Block I).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def scan_project(project_root: Path) -> tuple[int, list[str]]:
    project_root = project_root.resolve()
    src = project_root / "src"
    if not src.is_dir():
        return 1, [f"[FAIL] Kein src/-Verzeichnis unter {project_root}"]

    sys.path.insert(0, str(project_root))
    os.chdir(project_root)

    from src.logic_core.anti_heroin_validator import TrustCollapseException, validate_file

    errors: list[str] = []
    for f in sorted(src.rglob("*.py")):
        if "anti_heroin_validator.py" in str(f):
            continue
        try:
            validate_file(str(f))
        except TrustCollapseException as e:
            errors.append(f"Heroin detektiert in {f}: {e}")
    return (0 if not errors else 1), errors


def main() -> int:
    p = argparse.ArgumentParser(description="Anti-Heroin-Scan (src/)")
    p.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Projekt-Root (Default: cwd oder OMEGA_REPO)",
    )
    args = p.parse_args()
    root = args.root or Path(os.environ.get("OMEGA_REPO", ".")).resolve()
    code, errs = scan_project(root)
    for line in errs:
        print(line, file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
