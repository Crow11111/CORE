#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entfernt Plasma.Flex.Hub aus plasma-org.kde.plasma.desktop-appletsrc und
streicht die Applet-IDs aus allen AppletOrder-Zeilen.

Grund: Die Leiste verweist weiter auf das Plugin, obwohl der Ordner weg ist —
dann sucht Plasma unter plasmoids/ (inkl. *.bak) und erzeugt Terminal-Spam.

Vor dem Schreiben: gleiche Datei mit Endung .bak-OMEGA neben dem Original.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def applet_prefix(line: str) -> tuple[int, int] | None:
    m = re.match(
        r"^\[Containments\]\[(\d+)\]\[Applets\]\[(\d+)\]", line.strip()
    )
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def find_flex_hub_applets(lines: list[str]) -> set[tuple[int, int]]:
    bad: set[tuple[int, int]] = set()
    for i, line in enumerate(lines):
        s = line.strip()
        m = re.fullmatch(r"\[Containments\]\[(\d+)\]\[Applets\]\[(\d+)\]", s)
        if not m:
            continue
        c, a = int(m.group(1)), int(m.group(2))
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith("["):
            if lines[j].startswith("plugin="):
                if lines[j].split("=", 1)[1].strip() == "Plasma.Flex.Hub":
                    bad.add((c, a))
                break
            j += 1
    return bad


def strip_applet_order(line: str, remove_ids: set[str]) -> str:
    nl = "\n" if line.endswith("\n") else ""
    raw = line.rstrip("\n")
    if "AppletOrder=" not in raw or not remove_ids:
        return line
    key, _, rest = raw.partition("=")
    parts = [p for p in rest.split(";") if p.strip() and p.strip() not in remove_ids]
    return f"{key}={';'.join(parts)}{nl}"


def main() -> int:
    cfg = Path(
        os.environ.get(
            "PLASMA_APPLETSRC",
            Path.home() / ".config/plasma-org.kde.plasma.desktop-appletsrc",
        )
    )
    if not cfg.is_file():
        print(f"[ATLAS] Keine Datei: {cfg}", file=sys.stderr)
        return 1

    text = cfg.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)

    bad = find_flex_hub_applets(lines)
    if not bad:
        print("[ATLAS] Kein plugin=Plasma.Flex.Hub in der Leisten-Config — nichts zu tun.")
        return 0

    remove_ids = {str(a) for _, a in bad}
    print(f"[ATLAS] Entferne Plasma.Flex.Hub Applets (Containment,Applet): {sorted(bad)}")

    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        ap = applet_prefix(line)
        if ap is not None and ap in bad:
            i += 1
            while i < len(lines):
                L = lines[i]
                if not L.strip().startswith("["):
                    i += 1
                    continue
                ap2 = applet_prefix(L)
                if ap2 is not None and ap2 in bad:
                    i += 1
                    continue
                break
            continue
        if "AppletOrder=" in line:
            line = strip_applet_order(line, remove_ids)
        out.append(line)
        i += 1

    backup = cfg.with_name(cfg.name + ".bak-OMEGA")
    backup.write_text(text, encoding="utf-8")
    cfg.write_text("".join(out), encoding="utf-8")
    print(f"[ATLAS] Backup: {backup}")
    print(f"[ATLAS] Geschrieben: {cfg}")
    print("[ATLAS] Danach: plasmashell --replace")
    return 0


if __name__ == "__main__":
    sys.exit(main())
