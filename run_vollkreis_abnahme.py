#!/usr/bin/env python3
"""
Vollkreis-Abnahme: Alle Prüfungen aus OMEGA_VOLLKREIS_PLAN / BIBLIOTHEK.
Orchestrator führt dieses Skript selbst aus – kein Vertrauen ohne messbares Ergebnis.
Referenz: docs/05_AUDIT_PLANNING/OMEGA_VOLLKREIS_PLAN.md

Aufruf (aus Projekt-Root):
  .venv/bin/python run_vollkreis_abnahme.py
  python run_vollkreis_abnahme.py   (wenn venv aktiv)
  ./run_vollkreis_abnahme.py        (nach chmod +x; nutzt python3 aus PATH)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

def run(cmd: list[str] | str, timeout: int = 15, env: dict | None = None) -> tuple[int, str]:
    if isinstance(cmd, str):
        cmd = ["sh", "-c", cmd]
    env = env or os.environ
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT, env={**os.environ, **(env or {})})
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def check(name: str, ok: bool, detail: str = "") -> None:
    tag = "[PASS]" if ok else "[FAIL]"
    print(f"  {tag} {name}" + (f" — {detail}" if detail else ""))

def main() -> int:
    fails = 0
    print("=== VOLLKREIS-ABNAHME (Orchestrator prüft selbst) ===\n")

    # --- A: Dreadnought — Backend, Ports, Event-Bus ---
    print("A: Dreadnought (lokal)")
    code, out = run(["curl", "-s", "http://localhost:8000/status"], timeout=5)
    if code != 0:
        check("Backend /status erreichbar", False, out[:200] or "curl failed")
        fails += 1
    else:
        try:
            data = json.loads(out)
            eb = data.get("event_bus") or {}
            running = eb.get("running") is True
            check("Backend /status → event_bus.running true", running, str(eb) if not running else "")
            if not running:
                fails += 1
        except Exception as e:
            check("Backend /status JSON", False, str(e))
            fails += 1

    code, out = run("ss -tuln 2>/dev/null | grep -E ':8000|:3000' || true", timeout=3)
    ports_ok = "8000" in out and "3000" in out
    check("Ports 8000 + 3000 belegt", ports_ok, out.strip() if not ports_ok else "")
    if not ports_ok:
        fails += 1

    # Keine Windows-Pfade in zentralen Config-Skripten (beide prüfen falls vorhanden)
    config_checked = False
    for rel in ["src/config/core_path_manager.py", "src/config/core_state.py"]:
        pm = PROJECT_ROOT / rel
        if pm.exists():
            config_checked = True
            text = pm.read_text(encoding="utf-8", errors="replace")
            no_win = "C:\\\\" not in text and "c:\\\\" not in text and 'C:\\' not in text
            check(f"{rel} ohne Windows-Pfade", no_win)
            if not no_win:
                fails += 1
    if not config_checked:
        check("Config (core_path_manager oder core_state) vorhanden", (PROJECT_ROOT / "src/config").exists())
        if not (PROJECT_ROOT / "src/config").exists():
            fails += 1
    print()

    # --- B: Scout / HA ---
    print("B: Scout (HA)")
    ha_url = (os.getenv("HASS_URL") or "").strip().rstrip("/")
    ha_token = (os.getenv("HASS_TOKEN") or "").strip()
    if not ha_url or not ha_token:
        check("HA erreichbar (HASS_URL + HASS_TOKEN)", False, "fehlt in .env")
        fails += 1
    else:
        code, out = run([
            "curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}",
            "-H", f"Authorization: Bearer {ha_token}",
            f"{ha_url}/api/"
        ], timeout=10)
        ok = code == 0 and out.strip() == "200"
        check("HA API 200", ok, f"code={code} body={out[:100]}" if not ok else "")
        if not ok:
            fails += 1
    print()

    # --- C: VPS Kern ---
    print("C: VPS (Kern)")
    code, _ = run([sys.executable, "-m", "src.scripts.verify_vps_stack"], timeout=25)
    check("verify_vps_stack Exit 0", code == 0, f"exit {code}" if code != 0 else "")
    if code != 0:
        fails += 1
    print()

    # --- D: VPS Chroma Heartbeat (einzeln) ---
    print("D: VPS Chroma Heartbeat")
    vps = (os.getenv("VPS_HOST") or "").strip()
    chroma_port = os.getenv("CHROMA_PORT", "32768")
    if vps:
        code, out = run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://{vps}:{chroma_port}/api/v2/heartbeat"], timeout=8)
        ok = code == 0 and out.strip() == "200"
        check("Chroma v2 heartbeat 200", ok, f"exit={code} http={out}" if not ok else "")
        if not ok:
            fails += 1
    else:
        check("Chroma VPS (VPS_HOST gesetzt)", False, "VPS_HOST leer")
        fails += 1
    print()

    # --- E: Git / GitHub ---
    print("E: Git/GitHub")
    code, out = run("git remote -v 2>/dev/null | head -2", timeout=3)
    has_origin = "origin" in out and ("github.com" in out or "git@" in out)
    check("git remote origin (GitHub)", has_origin, out.strip() if not has_origin else "")
    if not has_origin:
        fails += 1
    # Push selbst nicht automatisch ausführen (Side Effect); nur Konfiguration
    print()

    # --- F: MCP Config vorhanden und atlas-remote konfiguriert ---
    print("F: MCP (Config)")
    mcp_cfg = PROJECT_ROOT / "mcp_remote_config.json"
    if mcp_cfg.exists():
        try:
            raw = mcp_cfg.read_text(encoding="utf-8", errors="replace")
            data = json.loads(raw)
            servers = data.get("mcpServers") or {}
            has_atlas = isinstance(servers, dict) and "atlas-remote" in servers
            ar = servers.get("atlas-remote") or {}
            has_cmd = ar.get("command") and ar.get("args")
            ok = has_atlas and has_cmd
            check("mcp_remote_config.json + atlas-remote (command/args)", ok, "" if ok else "atlas-remote oder command/args fehlt")
            if not ok:
                fails += 1
        except Exception as e:
            check("mcp_remote_config.json valid", False, str(e))
            fails += 1
    else:
        check("mcp_remote_config.json vorhanden", False)
        fails += 1
    print()

    # --- G: Substanz-Prüfungen (Agent-Pool, Multi-View, ChromaDB-Format) ---
    print("G: Substanz (Kernel-Mechanik)")

    code, out = run(["curl", "-s", "http://localhost:8000/status"], timeout=5)
    if code == 0:
        try:
            data = json.loads(out)
            pool_active = (data.get("agent_pool") or {}).get("active") is True
            check("Agent-Pool active=true", pool_active,
                  str(data.get("agent_pool")) if not pool_active else "")
            if not pool_active:
                fails += 1
        except Exception as e:
            check("Agent-Pool Status parsebar", False, str(e))
            fails += 1
    else:
        check("Backend fuer Pool-Check erreichbar", False)
        fails += 1

    code, out = run([sys.executable, "-m", "src.scripts.verify_multiview_pg"], timeout=25)
    mv_ok = code == 0 and "PASS" in out
    check("Multi-View pgvector (verify_multiview_pg)", mv_ok,
          out.strip()[:200] if not mv_ok else "")
    if not mv_ok:
        fails += 1

    code, out = run([sys.executable, "-c", """
import chromadb, os, json
from dotenv import load_dotenv
load_dotenv('/OMEGA_CORE/.env')
vps = os.getenv('VPS_HOST','').strip()
port = int(os.getenv('CHROMA_PORT','32768'))
c = chromadb.HttpClient(host=vps, port=port)
col = c.get_collection('events')
peek = col.peek(limit=3)
has_zero_vec = False
embeddings = peek.get('embeddings')
if embeddings is not None:
    for emb in embeddings:
        if emb is not None and all(float(v) == 0.0 for v in emb):
            has_zero_vec = True
            break
print(json.dumps({"count": col.count(), "has_zero_vectors": has_zero_vec}))
"""], timeout=15)
    if code == 0:
        try:
            info = json.loads(out.strip())
            no_zero = not info.get("has_zero_vectors", True)
            check("ChromaDB events: keine Zero-Vektoren", no_zero,
                  f"count={info.get('count')}, zero_vecs={info.get('has_zero_vectors')}")
            if not no_zero:
                fails += 1
        except Exception:
            check("ChromaDB events Format prüfbar", False, out[:200])
            fails += 1
    else:
        check("ChromaDB events erreichbar", False, out[:200])
        fails += 1
    print()

    # --- H: Integration (Zusammenfassung) ---
    print("H: Integration (Zusammenfassung)")
    if fails == 0:
        print("  [PASS] Alle Prüfungen bestanden. Geschlossene Kette messbar ok.")
    else:
        print(f"  [FAIL] {fails} Prüfung(en) fehlgeschlagen. Keine Abnahme.")
    print()
    return 0 if fails == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
