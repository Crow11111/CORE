#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entfernt Plasma-Applets anhand von plugin=… aus plasma-org.kde.plasma.desktop-appletsrc
und streicht die Applet-IDs aus allen AppletOrder-Zeilen.

Ohne Argumente: nur Plasma.Flex.Hub (Abwärtskompatibilität).

Beispiele:
  python3 plasma_entferne_flex_hub_applet.py org.kde.plasma.activitypager
  python3 plasma_entferne_flex_hub_applet.py Plasma.Flex.Hub org.kde.plasma.activitypager

Vor dem Schreiben: Backup plasma-org.kde.plasma.desktop-appletsrc.bak-OMEGA
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


def find_applets_with_plugins(lines: list[str], plugin_ids: set[str]) -> set[tuple[int, int]]:
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
                pid = lines[j].split("=", 1)[1].strip()
                if pid in plugin_ids:
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


def strip_config(lines: list[str], bad: set[tuple[int, int]]) -> list[str]:
    remove_ids = {str(a) for _, a in bad}
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
    return out


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

    plugin_ids = set(sys.argv[1:]) if len(sys.argv) > 1 else {"Plasma.Flex.Hub"}

    text = cfg.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)

    bad = find_applets_with_plugins(lines, plugin_ids)
    if not bad:
        print(f"[ATLAS] Kein Eintrag für plugin in {sorted(plugin_ids)} — nichts zu tun.")
        return 0

    remove_ids = {str(a) for _, a in bad}
    print(f"[ATLAS] Entferne Applets (Containment,Applet): {sorted(bad)} für {sorted(plugin_ids)}")

    out = strip_config(lines, bad)

    backup = cfg.with_name(cfg.name + ".bak-OMEGA")
    backup.write_text(text, encoding="utf-8")
    cfg.write_text("".join(out), encoding="utf-8")
    print(f"[ATLAS] Backup: {backup}")
    print(f"[ATLAS] Geschrieben: {cfg}")
    print("[ATLAS] Danach: plasmashell --replace")
    return 0


if __name__ == "__main__":
    sys.exit(main())
