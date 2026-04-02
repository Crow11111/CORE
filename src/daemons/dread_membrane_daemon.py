# -*- coding: utf-8 -*-
"""
Dreadnought Membrane: Schmerz-Flag (.py / Anti-Heroin + Syntax) und Planning-Flag (.md / [PASS]).
Kein Git-Revert, keine Quarantäne, keine Settle-Time — nur OS-Level-Flags unter /tmp/.
"""
from __future__ import annotations

import ast
import os
import sys
import time
from pathlib import Path

from loguru import logger

# CORE Imports
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from src.logic_core.anti_heroin_validator import TrustCollapseException, validate_file
except ImportError as exc:
    logger.error("anti_heroin_validator Import fehlgeschlagen: {}", exc)
    sys.exit(1)

# Überwachung: alle .py unter src/; alle .md in Planung + Architektur
SRC_ROOT = _REPO_ROOT / "src"
MD_ROOTS = (
    _REPO_ROOT / "docs" / "05_AUDIT_PLANNING",
    _REPO_ROOT / "docs" / "02_ARCHITECTURE",
)

PAIN_FLAG = Path("/tmp/omega_membrane_pain.flag")
PLANNING_FLAG = Path("/tmp/omega_membrane_planning.flag")

INTERVAL_SEC = 2.049  # asymmetrischer Takt (A5: nicht 2.0 exakt als „Mitte“)


def _is_py_path(path: Path) -> bool:
    """Nur echte .py-Endung (case-normalisiert), keine .py.txt-Loopholes über Suffix-Ketten."""
    name = path.name
    if not name.lower().endswith(".py"):
        return False
    # Kein zusätzliches Suffix nach .py (z. B. foo.py.bak)
    stem = path.stem
    return not stem.lower().endswith(".py")


def _is_md_path(path: Path) -> bool:
    name = path.name
    if not name.lower().endswith(".md"):
        return False
    stem = path.stem
    return not stem.lower().endswith(".md")


def iter_src_py_files() -> list[Path]:
    out: list[Path] = []
    if not SRC_ROOT.is_dir():
        return out
    for p in SRC_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts:
            continue
        if _is_py_path(p):
            out.append(p)
    return sorted(out)


def iter_md_files() -> list[Path]:
    out: list[Path] = []
    for root in MD_ROOTS:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if _is_md_path(p):
                out.append(p)
    return sorted(out)


def check_py_file(path: Path) -> tuple[bool, str | None]:
    """
    Returns (ok, reason_if_fail).
    Syntax zuerst (validate_file schluckt SyntaxError im Validator still).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"read_error:{exc}"

    try:
        compile(text, str(path), "exec", dont_inherit=True)
    except SyntaxError as exc:
        return False, f"syntax:{exc}"

    if "anti_heroin_validator.py" in path.name:
        return True, None

    try:
        validate_file(str(path))
    except TrustCollapseException as exc:
        return False, f"anti_heroin:{exc}"

    return True, None


def check_md_file(path: Path) -> str:
    """Returns 'PASS', 'LEGACY', or 'FAIL'."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "FAIL"

    if "[PASS]" in content:
        return "PASS"
    elif "[LEGACY_UNAUDITED]" in content:
        return "LEGACY"

    return "FAIL"


def set_pain_flag(reason_summary: str) -> None:
    try:
        PAIN_FLAG.parent.mkdir(parents=True, exist_ok=True)
        PAIN_FLAG.write_text(reason_summary[:2048] + "\n", encoding="utf-8")
    except OSError as exc:
        logger.error("Pain-Flag schreiben fehlgeschlagen: {}", exc)


def clear_pain_flag() -> None:
    try:
        PAIN_FLAG.unlink(missing_ok=True)
    except OSError as exc:
        logger.error("Pain-Flag löschen fehlgeschlagen: {}", exc)


def set_planning_flag(reason_summary: str) -> None:
    try:
        PLANNING_FLAG.parent.mkdir(parents=True, exist_ok=True)
        PLANNING_FLAG.write_text(reason_summary[:2048] + "\n", encoding="utf-8")
    except OSError as exc:
        logger.error("Planning-Flag schreiben fehlgeschlagen: {}", exc)


def clear_planning_flag() -> None:
    try:
        PLANNING_FLAG.unlink(missing_ok=True)
    except OSError as exc:
        logger.error("Planning-Flag löschen fehlgeschlagen: {}", exc)


class DreadnoughtMembrane:
    """
    Lokaler Wächter (Dreadnought): rekursiv alle src/**/*.py und docs/**/*.md
    in den definierten Wurzeln; Zustand nur über /tmp/*_flag.
    """

    def __init__(self) -> None:
        self.running = True
        logger.add("/tmp/dread_membrane.log", rotation="10 MB", level="INFO")
        logger.info(
            "Dreadnought Membrane gestartet (Pain={}, Planning={}). Repo={}",
            PAIN_FLAG,
            PLANNING_FLAG,
            _REPO_ROOT,
        )

    def evaluate_all_and_sync_flags(self) -> None:
        py_paths = iter_src_py_files()
        py_failures: list[str] = []
        for p in py_paths:
            ok, reason = check_py_file(p)
            if not ok:
                py_failures.append(f"{p.relative_to(_REPO_ROOT)}: {reason}")

        if py_failures:
            summary = "\n".join(py_failures[:64])
            if len(py_failures) > 64:
                summary += f"\n... +{len(py_failures) - 64} weitere"
            set_pain_flag(summary)
            logger.warning(
                "[MEMBRANE] Pain aktiv ({} fehlerhafte .py). Erste: {}",
                len(py_failures),
                py_failures[0],
            )
        else:
            clear_pain_flag()
            logger.debug("[MEMBRANE] Alle überwachten .py: Syntax + Anti-Heroin OK.")

        md_paths = iter_md_files()
        md_missing_pass: list[str] = []
        md_legacy: list[str] = []
        for p in md_paths:
            status = check_md_file(p)
            try:
                rel = p.relative_to(_REPO_ROOT)
            except ValueError:
                rel = p

            if status == "FAIL":
                md_missing_pass.append(str(rel))
            elif status == "LEGACY":
                md_legacy.append(str(rel))

        if md_missing_pass:
            summary = "\n".join(md_missing_pass[:64])
            if len(md_missing_pass) > 64:
                summary += f"\n... +{len(md_missing_pass) - 64} weitere"
            set_planning_flag(summary)
            logger.warning(
                "[MEMBRANE] Planning-Lock aktiv ({} .md ohne [PASS] oder Legacy). Erste: {}",
                len(md_missing_pass),
                md_missing_pass[0],
            )
        else:
            clear_planning_flag()
            if md_legacy:
                # Wir loggen die Info, aber setzen keinen Lock
                logger.debug(
                    "[MEMBRANE] Alle überwachten .md sind im Lock-Status OK. ({} Dokumente nutzen [LEGACY_UNAUDITED])",
                    len(md_legacy)
                )
            else:
                logger.debug("[MEMBRANE] Alle überwachten .md enthalten [PASS] oder keine .md.")

    def monitor(self) -> None:
        logger.info("Membrane-Loop: voller Scan alle {:.3f}s (kein Settle).", INTERVAL_SEC)
        while self.running:
            try:
                self.evaluate_all_and_sync_flags()
            except Exception:
                logger.exception("[MEMBRANE] Zyklus fehlgeschlagen")
            time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    membrane = DreadnoughtMembrane()
    try:
        membrane.monitor()
    except KeyboardInterrupt:
        logger.info("Membrane heruntergefahren.")
