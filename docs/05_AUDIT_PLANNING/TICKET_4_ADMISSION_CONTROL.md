# TICKET 4: Global Workspace & Admission Control (Phase 1)
**Status:** DRAFT (Warten auf O2 Audit)
**Typ:** Verification-First Specification

## 1. Architektonisches Ziel (Was bauen wir?)
Wir implementieren den fundamentalen Eintrittspunkt (Phase 1) der OMEGA Macro-Chain aus `MACRO_CHAIN_MASTER_DRAFT.md`.
Dies erfordert zwei Kernkomponenten:
1. **Das Global Workspace Schema (Postgres):** Die zentrale Tabelle, die als Ticket/Lock für alle Jobs dient und die Zustandsmaschine (`received` → `queued` → `processing` ...) abbildet.
2. **Die Admission Control (Spinal Reflex):** Die Logik-Weiche, die eingehende Reize anhand der *System-Drift $D$* bewertet und bei Annäherung an $D=0.951$ (Circuit Breaker) abblockt.

## 2. Hard Constraints & Axiome
- **A6 (Typ-Asymmetrie):** Die System-Drift $D$ und der Informationsgewinn $I$ müssen zwingend als `float` berechnet werden.
- **A5 (Asymmetrie-Verriegelung):** Die Drift $D$ wird geclampt auf `[0.049, 0.951]`. Der Wert $1.0$ (Symmetrie) ist verboten.
- **Latenz (Reflex-ACK):** Der Ingress (Phase 1) muss synchron extrem schnell sein. Die Berechnung von $D$ darf nicht blockieren (Lese $I$ aus Cache/Approximation).

## 3. Die Veto-Traps (Die Tests, die zuerst geschrieben werden müssen)

Der Producer muss zwingend zuerst die Test-Datei `tests/test_admission_control.py` schreiben. Diese muss folgende Traps enthalten:

### Trap 1: Der Drift-Kalkulator (A6, A5 & Jahn-Teller)
Die Funktion `calculate_system_drift(R: float, I: float) -> float` muss exakt die Formel $D = \text{clamp}(0.049, \frac{R}{I + 10^{-9}}, 0.951)$ abbilden UND den Symmetriebruch implementieren.
- *Test A (Basis):* `R=0.2, I=0.8` -> Drift muss korrekt berechnet werden.
- *Test B (A5-Schutz Oben):* `R=1.0, I=0.0` -> Darf nicht crashen (Division by Zero), muss bei exakt `0.951` kappen.
- *Test C (A5-Schutz Unten):* `R=0.0, I=0.951` -> Muss bei exakt `0.049` kappen.
- *Test D (Symmetriebruch / Anti-0.5):* Ergibt die Rechnung exakt `0.5` (oder liegt in einem Epsilon-Band von `0.499` bis `0.501`), MUSS die Funktion aktiv den Wert auf `0.51` snappen. `0.5` darf NIEMALS zurückgegeben werden.

### Trap 2: Der Circuit Breaker
Die Funktion `admission_check(drift: float) -> bool` entscheidet über Annahme.
- *Test A:* Wenn `drift < 0.90` -> Return `True` (Annahme).
- *Test B:* Wenn `drift >= 0.90` -> Return `False` (Abweisung, Circuit Breaker greift VOR dem harten Limit von 0.951, um Puffer zu haben).

### Trap 3: Global Workspace State Machine (Gerichtete Kausalität)
Das Modell für den `OmegaJob` mit der Funktion `transition_to(new_state: str)`.
- *Test A (Erlaubter Sprung):* Wechsel von `queued` zu `processing` muss erfolgreich sein.
- *Test B (Verbotener Kausal-Sprung):* Wechsel von `received` direkt zu `sent` MUSS eine harte `StateTransitionError` Exception werfen. Die Kette ist strikt gerichtet.

## 4. Instruktion für den Producer
Wenn O2 diesen Plan absegnet, wird der Producer-Agent aufgerufen.
**Schritt 1:** Schreibe `tests/test_admission_control.py` mit den obigen Veto-Traps.
**Schritt 2:** Schreibe `src/logic_core/admission_control.py` und das Job-Schema so, dass die Tests "PASS" zurückgeben.
**Schritt 3:** Nichts mocken. Nutze strikte `float` Typisierung.


[LEGACY_UNAUDITED]
