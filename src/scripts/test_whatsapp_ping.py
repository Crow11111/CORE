# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Sendet eine Test-WhatsApp über Evolution API (EvolutionClient),
um Erreichbarkeit und Konfiguration zu prüfen.
Ziel: WHATSAPP_TARGET_ID aus .env, sonst Fallback-JID wie test_whatsapp_closed_loop.
"""
import os
import sys
import uuid

os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

from src.network.evolution_client import EvolutionClient

PING_TEXT = "[CORE] Autarkie-Aktivierung: WhatsApp Ping erfolgreich. (Delta: 0.049)"
_FALLBACK_JID = "491788360264@s.whatsapp.net"


def _resolve_target() -> str:
    raw = (os.getenv("WHATSAPP_TARGET_ID") or "").strip().strip('"')
    return raw if raw else _FALLBACK_JID


def main() -> int:
    target = _resolve_target()
    trace_id = f"WA-PING-{uuid.uuid4().hex[:8].upper()}"

    client = EvolutionClient()
    if not client.is_configured():
        print("FEHLER: EvolutionClient nicht konfiguriert (EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE).")
        return 1

    print(f"Trace: {trace_id}")
    print(f"Ziel: {target!r}")
    print(f"Text: {PING_TEXT!r}")

    ok = client.send_whatsapp_sync(to_number=target, text=PING_TEXT, trace_id=trace_id)
    print("Ergebnis:", "OK (Evolution API hat 200/201 geliefert)" if ok else "FEHLER")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
