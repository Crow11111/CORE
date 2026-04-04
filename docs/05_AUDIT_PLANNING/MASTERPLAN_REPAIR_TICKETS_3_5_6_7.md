# MASTERPLAN: REPAIR TICKETS 3, 5, 6, 7

**Vector:** 2210 (Execution) | **Status:** ACTIVE
**Orchestrator:** Ring 0 (OMEGA)
**Ziel:** Radikal saubere, deterministische und zero-trust konforme Behebung der VETOs aus dem O2-Audit für die Tickets 3, 5, 6 und 7.

## PHASE 1: TICKET 5, 6, 7 (LOGIC CORE REPAIRS)
Die Module im `logic_core` haben spezifische Axiom-Lücken, die parallel von Sub-Agenten geschlossen werden.

### Ticket 5 (Arbitration)
**Team Lead:** Core Logic Engineer
- **Befund O2:** Postgres Global Workspace wird durch ein `_completed_jobs` Set gefaket. Zustände wie `efference_submitted` oder `blocked_on_evidence` werden nicht physisch in einer DB/einem echten Job-Objekt gesetzt.
- **Maßnahme:** `src/logic_core/arbitration_engine.py` umschreiben. Es muss ein realistischer DB- oder State-Update stattfinden (Mocking der echten Postgres-Schnittstelle im Test ist erlaubt, aber der Aufruf einer Update-Funktion muss passieren). Status MUSS physisch als String im Job oder via DB-Call mutiert werden. Tests anpassen!

### Ticket 6 (Efference Veto)
**Team Lead:** Security & Crypto Expert
- **Befund O2:** `attractor_evaluate` verifiziert die `signature` der Efferenzkopie nicht. Axiom A7 (Zero-Trust) gebrochen.
- **Maßnahme:** `src/logic_core/efference_veto.py` und `tests/test_efference_veto.py` umschreiben. Die Signatur der Kopie muss kryptografisch oder logisch streng geprüft werden. Ein Fehlschlag der Signatur MUSS in einem VetoToken oder TrustCollapse enden.

### Ticket 7 (Temporal Alignment)
**Team Lead:** Mathematics & Core Logic
- **Befund O2:** `apply_kardanic_rescue` gibt als P-Vektor (int) hart `1` zurück statt eines Counters. `dispatch_to_evolution` akzeptiert jedes Objekt `!= None`.
- **Maßnahme:** `src/logic_core/temporal_alignment.py` und `tests/test_temporal_alignment.py` anpassen. Der P-Vektor muss inkrementiert werden (State/Counter). `dispatch_to_evolution` MUSS auf exakt den Typ `ReleaseToken` prüfen (A7 Typ-Kontrakt).

## PHASE 2: TICKET 3 (EXISTENTIAL PACEMAKER VAR_3)
**Team Lead:** Neuromorphic Biology Expert
- **Befund O2:** Code und Tests nutzen die veraltete `SPEC_PACEMAKER_FINAL` Baseline, ignorieren `SPEC_PACEMAKER_VAR_3.md` (Exponentieller Decay, W=17 Fenster, RMSSD, Monotonie-Boost, Pathologie-Log).
- **Maßnahme:** KOMPLETTER REWRITE von `src/daemons/omega_pacemaker.py` und `tests/test_pacemaker.py` auf Basis von `docs/05_AUDIT_PLANNING/SPEC_PACEMAKER_VAR_3.md`.
- AC-V3-1 bis AC-V3-7 müssen strikt programmiert und in Verification-First Traps abgeprüft werden.

## PHASE 3: O2 ZERO-CONTEXT RE-AUDIT
Sobald alle Tickets repariert und die Tests PASS sind, wird O2 (Hugin) erneut gerufen.
