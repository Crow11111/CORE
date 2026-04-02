# TICKET 6: Efference Copy & Veto-Fenster (Phase 3 & 4)
**Status:** DRAFT (Warten auf O2 Audit)
**Typ:** Verification-First Specification

## 1. Architektonisches Ziel (Was bauen wir?)
Wir implementieren Phase 3 und 4 der Macro-Chain: Das Forward Model und den "Point of No Return".
Bevor OCBrain eine Aktion in die Außenwelt feuert (Evolution API), MUSS es eine Vorhersage (Efferenzkopie) an den lokalen Attractor schicken.
1. **Die Efferenzkopie:** Ein starrer Datenkontrakt.
2. **Das Veto-Fenster:** Der OMEGA_ATTRACTOR prüft die Kopie blitzschnell auf harte Axiom-Verletzungen.
3. **Point of No Return:** Nur bei einem "Release" vom Attractor darf der Zustand auf die Außenwelt überspringen.

## 2. Hard Constraints & Axiome
- **Axiom 7 (Zero-Trust):** Der Attractor vertraut der Efferenzkopie nicht blind. Er prüft die kryptografische Signatur und die Einhaltung der A1/A5 Grenzen.
- **Kausalität:** `processing` → `efference_submitted` → `vetoed` ODER `released`.
- **Typ-Asymmetrie (A6):** Zeitstempel und Konfidenz in der Kopie sind `float`.

## 3. Die Veto-Traps
Die Test-Datei `tests/test_efference_veto.py` muss zwingend zuerst vom Producer geschrieben werden.

### Trap 1: Efferenzkopie-Kontrakt & Immutability
Die Funktion `create_efference_copy(correlation_id: str, proposed_action: dict, expected_outcome: dict, expected_arrival: float, signature: str) -> object`.
- *Test A (Pflichtfelder):* Das Fehlen eines Feldes (insbesondere `expected_outcome` für späteres Lernen) führt zu einem harten `ValueError`.
- *Test B (Immutability):* Ein Versuch, die erstellte Efferenzkopie nachträglich zu verändern (z.B. `copy.expected_arrival = 9.9`), MUSS zwingend eine Exception (z.B. `FrozenInstanceError` bei Dataclasses) werfen.

### Trap 2: Attractor Veto-Fenster (Zero-Trust & Idempotenz)
Die Funktion `attractor_evaluate(copy: object, local_trust_level: float, history_ids: set) -> object`.
- *Test A (Release Token):* Wenn `local_trust_level > 0.049`, die Signatur stimmt und die ID neu ist, gib ein kryptografisch versiegeltes `ReleaseToken` (enthält Hash der `proposed_action`) zurück.
- *Test B (Veto durch Trust-Collapse):* Wenn `local_trust_level <= 0.049`, MUSS der Attractor ein `VetoToken` zurückgeben.
- *Test C (Veto durch Asymmetrie-Bruch):* Wenn in der `proposed_action` `0.5`, `1.0` oder `0.0` vorkommen (Verstoß gegen A5), MUSS der Attractor ein `VetoToken` zurückgeben.
- *Test D (Idempotenz / Anti-Replay):* Wenn die `correlation_id` der Efferenzkopie bereits in `history_ids` existiert, MUSS ein `ReplayConflictError` geworfen werden (409 Conflict Simulation).
- *Test E (Asynchrones Schmerz-Signal):* Bei jedem Veto (Test B und C) MUSS der Attractor garantieren, dass ein asynchrones Signal an OCSpline abgesetzt wird (`dispatch_pain_signal`). Das Auslösen dieser Funktion muss über einen Test-Spy verifiziert werden, ohne die synchrone Rückgabe des `VetoTokens` zu blockieren.

### Trap 3: Point of No Return (Kryptografische Kausalitäts-Wand)
Die Funktion `execute_action(action: dict, release_token: object) -> bool`.
- *Test A (Erlaubt):* Nur wenn ein valides `ReleaseToken` übergeben wird UND der Hash im Token exakt mit der `action` übereinstimmt, darf die Funktion `True` zurückgeben.
- *Test B (Verboten):* Wenn ein `VetoToken` übergeben wird oder der Hash der `action` nicht zum `ReleaseToken` passt (Tampering), MUSS die Ausführung mit einem `PointOfNoReturnError` hart geblockt werden.

## 4. Instruktion für den Producer
Nach dem PASS von O2:
**Schritt 1:** Schreibe `tests/test_efference_veto.py`.
**Schritt 2:** Schreibe `src/logic_core/efference_veto.py`.
**Schritt 3:** Verifiziere das Modul via `anti_heroin_validator.py`.
**Schritt 4:** Inventar aktualisieren.


[LEGACY_UNAUDITED]
