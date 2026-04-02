# TICKET 5: Global Workspace Arbitration & Liveness (Phase 2)
**Status:** DRAFT (Warten auf O2 Audit)
**Typ:** Verification-First Specification

## 1. Architektonisches Ziel (Was bauen wir?)
Wir implementieren Phase 2 der Macro-Chain: Die Arbitration (Konfliktauflösung) im Global Workspace (Postgres) und die Überwachung der asynchronen Kognitions-Jobs.
Drei Kernmechanismen müssen gegossen werden:
1. **Multi-Job Konkurrenz (Scheduler):** Zuteilung freier Worker nach `priority` (als `int`), ohne laufende Jobs zu killen.
2. **Single-Job Merge (Kollisionsauflösung):** Parallele Berechnungen desselben Jobs konkurrieren. Der erste valide Commit gewinnt. Nachzügler werden strikt abgelehnt.
3. **Liveness & A10 (Occam's Negative Razor):** Jobs müssen einen Heartbeat senden. Bleibt dieser aus, stirbt der Job. Wenn die lokale Evidenz erschöpft ist, greift A10 (Stopp und Operator-Eskalation).

## 2. Hard Constraints & Axiome
- **A10 (Occam's Negative Razor):** Harter Interrupt bei Evidenz-Erschöpfung. Keine Halluzination, kein ungerichtetes Raten. Status zwingend auf `blocked_on_evidence`.
- **A6 (Typ-Asymmetrie):** `priority` und Zähler sind `int`. Latenzen, Timestamps und Konfidenzwerte sind `float`.
- **Zustandsmaschine:** Es gilt die in Ticket 4 definierte Kausalität.

## 3. Die Veto-Traps (Veto-Gates)
Der Producer muss die Test-Datei `tests/test_arbitration.py` erstellen, bevor der Code implementiert wird.

### Trap 1: Priority Scheduler (A6)
Die Funktion `get_next_job(queue: list, available_workers: int) -> list` wählt den nächsten Job.
- *Test A (Priority & Arrival):* Die Jobs müssen zwingend nach `priority` (int, 1 ist High) UND sekundär nach `expected_arrival` (float, frühe Deadline zuerst) absteigend sortiert werden.
- *Test B (Starvation Protection):* Ein bereits `processing` Job darf NICHT abgebrochen/ersetzt werden, nur weil ein neuer High-Priority Job hinzukommt.

### Trap 2: Single-Job Merge Rule (First-Wins & Jahn-Teller)
Die Funktion `commit_job_result(job_id: str, result_data: dict, resonance_confidence: float) -> bool`.
- *Test A (First Commit):* Der erste Aufruf mit ausreichender Konfidenz (und nicht im toten 0.5 Band) setzt den Zustand auf `efference_submitted` und speichert das Resultat. Return `True`.
- *Test B (Late Arriver):* Ein zweiter Aufruf für *denselben* `job_id` MUSS mit einem `MergeConflictError` abgewiesen werden. Return `False`.
- *Test C (Jahn-Teller-Symmetriebruch / Anti-0.5):* Konvergiert die `resonance_confidence` in das probabilistische Entropiemaximum ($0.49 \le \text{confidence} \le 0.51$), droht der statische Tod. Der Commit MUSS mit einem `EntropicDeadlockError` abgewiesen oder hart terminiert werden. Kein Merge erlaubt!

### Trap 3: Liveness Monitor (Heartbeat)
Die Funktion `check_liveness(job_id: str, last_heartbeat: float, current_time: float, timeout: float) -> str`.
- *Test A (Alive):* `current_time - last_heartbeat < timeout` -> Job bleibt `processing`.
- *Test B (Dead):* `current_time - last_heartbeat >= timeout` -> Job-Status wechselt zwingend auf `failed` (Kardanische Zeitüberschreitung).

### Trap 4: A10 Occam's Negative Razor (Evidenz & PE)
Die Funktion `evaluate_evidence(job_id: str, available_vectors: int, internal_prediction_error: float) -> str`.
- *Test A (Ausreichend Evidenz):* `available_vectors > 0` UND `internal_prediction_error < 0.8` -> Job läuft normal weiter.
- *Test B (Evidenz erschöpft):* `available_vectors == 0` -> Funktion MUSS den Status des Jobs zwingend auf `blocked_on_evidence` setzen (Operator-Eskalation).
- *Test C (Hoher PE):* Selbst wenn Vektoren existieren (`available_vectors > 0`), aber der interne Prediction Error zu hoch ist (`internal_prediction_error >= 0.8`), greift A10 sofort. Status: `blocked_on_evidence`. Kein Halluzinieren!

## 4. Instruktion für den Producer
Wenn O2 diesen Plan absegnet:
**Schritt 1:** Schreibe `tests/test_arbitration.py`.
**Schritt 2:** Schreibe `src/logic_core/arbitration_engine.py` so, dass die Tests bestehen.
**Schritt 3:** Verifiziere das Modul via `anti_heroin_validator.py`.
**Schritt 4:** Inventar aktualisieren.


[LEGACY_UNAUDITED]
