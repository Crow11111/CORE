# TICKET 8: Biometrische Drift-Erfassung (Audio-Visual Telemetry)
**Status:** DRAFT (Warten auf O2 Audit)
**Typ:** Verification-First Specification

## 1. Architektonisches Ziel (Was bauen wir?)
Wir implementieren die biometrische Telemetrie-Auswertung gemäß dem Architektur-Entwurf (`docs/05_AUDIT_PLANNING/CONCEPT_AUDIO_VISUAL_PREDICTION.md`). Ziel ist die präemptive Erkennung von Hyperfokus, kognitiver Dissonanz und physischer Erschöpfung des biologischen Motors (Marc). Die Architektur stützt sich auf dezentrale Sensordaten (Blink-Rate, Frown-Blendshapes) aus dem Event-Bus und interveniert in drei Stufen, um den Kausal-Kollaps abzufangen.

## 2. Hard Constraints & Axiome
- **A5 (Baryonisches Delta):** Alle Schwellwerte und Deltas für Stress-Indikatoren (Blink-Rate, Frown) unterliegen den Axiomen. `0.0`, `0.5` und `1.0` sind absolut VERBOTEN. Ein Delta der Baseline muss immer geklappt werden (Minimum $0.049$).
- **Typ-Asymmetrie (A6):** Biometrische Signale (EAR, Blendshape-Deltas, Frown) sind zwingend `float`. Event-Counter (z.B. Anzahl der Events) sind zwingend `int`.
- **Die 3-Stufen Intervention (Asymmetrischer Trust-Routing Ansatz):**
  1. *Subkutan:* Anpassung der Umgebung (ohne Agenten-Output).
  2. *Sanfter Riss:* TTS-Intervention (Audio).
  3. *Gravitativer Schnitt:* Harte Veto-Sperre im Code-Prozess.

## 3. Die Veto-Traps (Veto-Gates)
Der Producer muss die Test-Datei `tests/test_biometric_telemetry.py` schreiben.

### Trap 1: Baseline & Delta-Kalkulation (A5 Clamp)
Die Funktion `calculate_biometric_delta(current_state: dict, baseline: dict) -> float`.
- *Test A (Stabiler Zustand):* `current_state` (z.B. 12 Blinks, Frown 0.09) entspricht `baseline`. Return = `0.049` (Baryonisches Minimum, niemals `0.0`).
- *Test B (Extremer Hyperfokus):* Blink-Rate fällt rapide (z.B. < 1.0), Frown steigt signifikant (> 0.3). Das Delta steigt, darf aber NIEMALS `0.5` oder `1.0` zurückgeben. Max Delta ist `0.951`.
- *Typ-Prüfung:* Der berechnete Wert ist exakt ein `float`.

### Trap 2: Spike-Detection & Event-Aggregation
Die Funktion `evaluate_event_spikes(event_buffer: list, delta_threshold: float) -> tuple[bool, int]`.
- *Test A (Rauschen ignorieren):* Wenn die Events (Audio, Maus, Blendshape) unterhalb des `delta_threshold` liegen, wirft die Funktion ein "No-Spike". Return `(False, 0)`.
- *Test B (Kritische Überlappung):* Audio-Spike (Seufzen) + Frown-Spike fallen zeitlich zusammen und überschreiten den `delta_threshold`. Die Funktion triggert ein True. Der `int` Rückgabewert ist die Aggregations-Masse der kombinierten Events (Typ-Asymmetrie). Return `(True, int)`.

### Trap 3: Anti-Hyperfokus Interventions-Stufen
Die Funktion `determine_intervention_level(delta: float, session_duration: int) -> int`.
- *Test A (Subkutan):* Wenn `delta > 0.049` und `< 0.382`, Return Level = `1` (Licht, Sounds).
- *Test B (Sanfter Riss):* Wenn `delta >= 0.382` und `< 0.951` UND `session_duration > 60` (Zeit-Vektor), Return Level = `2` (TTS).
- *Test C (Gravitativer Schnitt / Veto):* Wenn `delta == 0.951` (Maximaler Schmerz / Bruch), MUSS Level = `3` (Veto-Sperre) zurückgegeben werden.

## 4. Instruktion für den Producer
Wenn O2 diesen Plan absegnet:
**Schritt 1:** Schreibe `tests/test_biometric_telemetry.py` mit den obigen Veto-Traps.
**Schritt 2:** Schreibe `src/logic_core/biometric_telemetry.py`, um die Tests zu erfüllen.
**Schritt 3:** Verifiziere das Modul via `anti_heroin_validator.py`.
**Schritt 4:** Inventar und Session-Log (docs/05_AUDIT_PLANNING) aktualisieren.


[LEGACY_UNAUDITED]
