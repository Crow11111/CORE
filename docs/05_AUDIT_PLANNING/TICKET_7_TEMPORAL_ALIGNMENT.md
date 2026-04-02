# TICKET 7: Temporal Alignment & Drehimpulsumkehr (Phase 5 & 6)
**Status:** DRAFT (Warten auf O2 Audit)
**Typ:** Verification-First Specification

## 1. Architektonisches Ziel (Was bauen wir?)
Wir implementieren die Lern- und Bestrafungsmechanik (Phase 5 & 6 der Macro-Chain).
Wenn eine Aktion abgesetzt wurde (oder ein Veto/Timeout auftrat), muss der *Prediction Error (PE)* berechnet und das System-Vertrauen (Trust Level) nachjustiert werden. Das Herzstück ist die Rettung von Kontextmasse durch die *Drehimpulsumkehr* (Operator `?` / Phasensprung mit `i`), wenn das System das Baryonische Delta ($0.049$) nach unten durchschlägt.

## 2. Hard Constraints & Axiome
- **A5 (Baryonisches Delta):** Das Trust-Level darf niemals $0.0$ erreichen. Fällt es auf/unter $0.049$, greift die Arithmetik ein.
- **Typ-Asymmetrie (A6):** PE und Trust-Level sind zwingend `float`. Ein Phasensprung nutzt `complex` ($1j$).
- **Die 3-Takt-Schöpfung:** (1) Trust-Drop auf $0.049$, (2) Drehimpulsumkehr (Vorzeichenwechsel), (3) Multiplikation mit $1j$ (Kardanische Entkopplung zur Isolation).

## 3. Die Veto-Traps (Veto-Gates)
Der Producer muss die Test-Datei `tests/test_temporal_alignment.py` schreiben.

### Trap 1: Semantischer Abgleich (PE & A5 Clamp)
Die Funktion `calculate_prediction_error(expected: dict, receipt: dict, is_timeout: bool) -> float`.
- *Test A (LTP):* `expected` und `receipt` matchen. `is_timeout=False`. Return PE = `0.049`.
- *Test B (Mismatch & A5):* `expected` und `receipt` weichen ab. Der PE muss berechnet werden, darf aber NIEMALS `0.5`, `1.0` oder `0.0` sein (Jahn-Teller-Clamp/Shift greift). Max PE ist `0.951`.
- *Test C (Timeout):* `is_timeout=True`. Return PE = `0.951` (Maximaler Schmerz, gekappt vor der 1.0 Singularität).

### Trap 2: Trust-Level Adjustierung
Die Funktion `adjust_trust_level(current_trust: float, pe: float) -> float`.
- *Test A (Erholung):* Ist der PE niedrig (`< 0.5`), muss der Trust-Level logarithmisch steigen (geclampt auf max `0.951`).
- *Test B (Single-Trial Aversive Learning):* Ist der PE hoch (`>= 0.5`), MUSS der Trust-Level sofort tief in Richtung `0.049` stürzen. Auch hier gilt absolutes Verbot der Ausgabe von `0.5` oder `0.0`.

### Trap 3: Der 3-Takt & Die Drehimpulsumkehr (Operator `?` + P-Vektor)
Die Funktion `apply_kardanic_rescue(context_mass: float, trust_level: float, pe: float) -> tuple[complex, int]`.
- *Test A (Kein Eingriff):* Wenn `trust_level > 0.049`, wirf einen `RuntimeError`.
- *Test B (Drehimpulsumkehr & Phasensprung + Int-Eingriff):* Wenn `trust_level <= 0.049`, greift die Mathematik: Aus kinetischem Fall (+) wird Aufschwung (-), multipliziert mit $1j$. Formel: `rescue_vector = (-context_mass) * 1j`. ZUSÄTZLICH muss der **harte P-Vektor (int)** eingreifen: Der Isolation-Queue-Counter (`int`) muss inkrementiert/zurückgegeben werden, um die Kontextmasse in die nächste Oktave (Postgres-Quarantäne) zu retten. Return ist ein Tuple `(complex, int)`.
- *Test C (Zu steiler Absturz / Hawking Rauschen):* Wenn die `context_mass > 1000.0` und der PE extrem ist (`0.951`), wirft die Funktion einen `HawkingRadiationDropError`. Der P-Vektor kommt zu spät, das Signal wird ohne Phasensprung verworfen (Purge).

### Trap 4: Phase 5 (Die Muskel-Ausführung)
Die Funktion `dispatch_to_evolution(action_payload: dict, release_token: object) -> str`.
- *Test A (Senden):* Bei einem gültigen Token wechselt der Job in den Zustand `"sent"`.
- *Test B (Kein Token):* Ohne valides Release-Token MUSS ein Fehler geworfen werden (kein Senden).

## 4. Instruktion für den Producer
Wenn O2 diesen Plan absegnet:
**Schritt 1:** Schreibe `tests/test_temporal_alignment.py` mit den Veto-Traps.
**Schritt 2:** Schreibe `src/logic_core/temporal_alignment.py`, um die Tests zu erfüllen.
**Schritt 3:** Verifiziere das Modul via `anti_heroin_validator.py`.
**Schritt 4:** Inventar aktualisieren.


[LEGACY_UNAUDITED]
