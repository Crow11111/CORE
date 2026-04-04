# MASTERPLAN: TICKET 11 EXECUTION (COGNITIVE MEMBRANE)

**Vector:** 2210 (Execution) | **Status:** ACTIVE
**Orchestrator:** Ring 0 (OMEGA)
**Ziel:** Radikal saubere, deterministische und zero-trust konforme Umsetzung der 4 Säulen aus TICKET_11_COGNITIVE_MEMBRANE.md.

## PHASE 1: INFRASTRUKTUR & EVENT SOURCING (VPS / MCP)
**Team Lead:** Infrastructure & DB Architect
**Ziele:**
1. **PostgreSQL Event Store:** Erweitern des bestehenden Schemas (`src/db/core_infrastructure.sql` / `multi_view_client.py`) um eine echte, append-only Event-Tabelle für die chronologische Historie.
2. **MCP Server (`user-omega-state-mcp`):** Implementieren der neuen Tools `get_episodic_history` (für den Pre-Flight) und `record_event` (für den Abschluss).
**Abnahme:** MCP-Server liefert chronologische Historie lokal an Cursor.

## PHASE 2: PRE-FLIGHT & APOPTOSE (DREADNOUGHT MEMBRANE)
**Team Lead:** Core Logic & Daemon Engineer
**Ziele:**
1. **Pre-Flight Trap:** Implementierung von `validate_agent_preflight` in `anti_heroin_validator.py`. Verlangt zwingend einen `memory_hash` via MCP-Abfrage. Wirft `PreFlightVetoException` bei Fehlen.
2. **Apoptose & Kardanik:** Implementierung von `trigger_apoptosis` in `dread_membrane_daemon.py`. Prüft Entropie strikt gegen $\Delta = 0.049$ und löscht Noise-Events nur unterhalb dieser Schwelle (Säule 4).
**Abnahme:** `pytest tests/test_ticket_11.py` wechselt von FAIL (Heroin-frei) auf PASS.

## PHASE 3: CONTEXT FORCING (WATCHDOG)
**Team Lead:** Integration & Telemetry Specialist
**Ziele:**
1. **Watchdog Daemon:** Erstellung/Erweiterung des `omega-watchdog` Daemons.
2. **Dynamische Injektion:** Der Watchdog pollt via MCP die kritischen "Lessons Learned" und schreibt sie dynamisch in eine `cursor_status.md` (oder injiziert sie ins Terminal), um Attention Dilution zu verhindern (Säule 3).
**Abnahme:** Watchdog läuft als Hintergrundprozess und aktualisiert die Datei basierend auf MCP-Events.

## PHASE 4: VOLLKREIS-AUDIT (O2)
**Team Lead:** Orchestrator B (O2 / Hugin)
**Ziele:**
1. Zero-Context Audit der gesamten Implementierung.
2. Prüfung der Interaktion mit bestehenden Tickets (Ticket 8, 9, 10).
3. Verifikation der Einhaltung aller Axiome (A6 Float/Int Trennung, A7 Zero-Trust).
**Abnahme:** O2 erteilt finalen System-PASS.

---
*Orchestrator A delegiert strikt an spezialisierte Sub-Agenten und überwacht die Meilensteine.*