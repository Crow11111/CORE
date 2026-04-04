# -*- coding: utf-8 -*-
"""
Zero-Trust: Doku-Drift — Chroma-VPS-Port 32768 (Legacy) vs. Vertrag 32779.

Überspringt Audio/Kontext-Literale (32768.0), Ollama-Kontext, aggregierte Master-Artefakte.
Exit 1 bei Treffer → WP-DOK-DRIFT Abnahme-Helfer.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DOCS = _PROJECT_ROOT / "docs"

# Zeilen mit diesen Fragmenten sind erlaubt (kein Chroma-Host-Port)
_LINE_OK_SUB = (
    "32768.0",
    "int16Array",
    "float32Array",
    "OMEGA_COUNCIL_NUM_CTX",
    "NUM_CTX",
    "65536",
    "49152",
    "16384",
    "VRAM",
    "Legacy 32768",
    "historisch 32768",
    "32768 Legacy",
    "nicht mehr zwingend 32768",
    "älteren Tabellen",
    "Doku-Legacy",
    "WP-DOK-DRIFT",
)

# Pfade: historische Snapshots / generierte Megadateien
_PATH_SKIP_PARTS = (
    "docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2",
    "REALITY_CHECK_VPS_TICKETS.md",
    "Bereich_A_Dreadnought_Abnahme.md",
    "/00_CORE_INFRASTRUCTURE_MASTER.md",
    "/00_CORE_ARCHITECTURE_MASTER.md",
    "cursor_status.md",
    "DEEP_RESEARCH_PROMPT_KAUSALITAET.md",
)

# Chroma/VPS-Kontext mit falscher Host-Port-Angabe 32768
_BAD = re.compile(
    r"(?:"
    r":32768/api|"
    r"VPS_HOST.\{?\}??:32768|"
    r"CHROMA_PORT[^\n]{0,24}32768|"
    r"CHROMA_PORT\s*=\s*32768|"
    r"CHROMA_PORT',\s*'32768'|"
    r"chromadb[^\n]{0,30}32768|"
    r"Chroma v2\s*:32768|"
    r"curl[^\n]{0,50}32768[^\n]{0,30}heartbeat"
    r")",
    re.IGNORECASE,
)


def main() -> int:
    bad_hits: list[str] = []
    if not _DOCS.is_dir():
        print("[FAIL] docs/ fehlt")
        return 1
    for path in sorted(_DOCS.rglob("*.md")):
        rel = str(path.relative_to(_PROJECT_ROOT)).replace("\\", "/")
        if any(part in rel for part in _PATH_SKIP_PARTS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            bad_hits.append(f"{rel}: read error {e}")
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if "32768" not in line:
                continue
            if any(s in line for s in _LINE_OK_SUB):
                continue
            if _BAD.search(line):
                bad_hits.append(f"{rel}:{i}: {line.strip()[:160]}")
    if bad_hits:
        print("[FAIL] Chroma/VPS-Doku-Drift (32768):")
        for h in bad_hits[:80]:
            print(" ", h)
        if len(bad_hits) > 80:
            print(f"  ... +{len(bad_hits) - 80} weitere")
        return 1
    print("[OK] Keine verdächtigen Chroma-32768-Zeilen in docs/ (gefiltert)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
