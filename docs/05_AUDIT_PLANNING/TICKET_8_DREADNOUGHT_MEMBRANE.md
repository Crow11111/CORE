# TICKET 8: Dreadnought Membrane (Schmerz & Kognitive Blockade statt Amputation)

## 1. Das Problem (Der Amputations-Fehler & Naming-Loophole)
Der erste (unautorisierte) Entwurf des `dread_membrane_daemon` leidet unter zwei fatalen Konstruktionsfehlern, die gegen die biologische Logik und das Zero-Trust Prinzip (Axiom A7) verstoßen:
1. **Die 10-Sekunden-Guillotine (Human-Hostility):** Ein statisches Timing löscht/revertiert Dateien, während der Operator noch tippt (Nachdenk-Pause). Das System "amputiert" den Arm bei einem fehlerhaften Nervensignal, statt Schmerz zu induzieren, bis der Fehler behoben ist.
2. **Das Naming-Loophole:** Die Heuristik für Audit-Pläne prüft nur auf `CONCEPT_` oder `MACRO_`. Ein korrumpierter Agent könnte einfach eine `test.txt` oder `X_ARCH.md` schreiben und die Fessel komplett umgehen.

## 2. Die biologische & physikalische Lösung
Statt lokaler Amputation (Löschung/Revert) induziert die Membrane **systemischen Schmerz und Lähmung**, bis die topologische Kausalität (Anti-Heroin / O2-PASS) wiederhergestellt ist.

### Regel 1: Totale Abdeckung (Keine Loopholes)
- Die Membrane überwacht rekursiv **ALLE** `.py` Dateien in `src/` (kein Bypass durch Umbenennung).
- Die Membrane überwacht rekursiv **ALLE** `.md` Dateien in `docs/05_AUDIT_PLANNING/` und `docs/02_ARCHITECTURE/`.

### Regel 2: Schmerz-Modus statt Löschung (Für `.py` Dateien)
Wenn eine `.py` Datei den `anti_heroin_validator.py` nicht besteht:
- **Aktion:** Die Datei wird NICHT gelöscht.
- **Konsequenz:** Die Membrane erzeugt ein OS-Level Pain-Flag (`/tmp/omega_membrane_pain.flag`).
- **Wirkung auf CORE:** Solange dieses Flag existiert, erzwingt die Admission Control (Phase 1) einen System-Drift von `0.951` (Maximaler Schmerz). Das System lehnt alle neuen Jobs ab. Erst wenn der Operator/Agent den Code repariert und der Validator ihn freigibt, wird das Flag gelöscht und der Schmerz endet.

### Regel 3: Kognitive Blockade (Für `.md` Dateien)
Wenn eine `.md` Datei im Planungs-Ordner editiert wird und den String `[PASS]` (O2-Freigabe) NICHT enthält, handelt es sich um einen unfertigen Plan (Draft).
- **Biologische Entsprechung:** Das System "denkt" gerade (Planning Phase). Während das Gehirn intensiv plant, inhibiert es den Motorcortex, um unkontrollierte Ausführungen zu verhindern.
- **Aktion:** Die Membrane setzt ein Cognitive-Lock-Flag (`/tmp/omega_membrane_planning.flag`).
- **Wirkung:** Das System kann weiterhin kommunizieren (LLM Chat), aber physische Ausführungen (Phase 5 Muskel-Ausführung) werden blockiert (bzw. auf Eis gelegt). Sobald das Dokument ein `[PASS]` erhält (O2 hat den Plan abgesegnet), wird der Lock aufgehoben.

## 3. Veto-Traps (Verification-First für den Producer)
Der Producer muss folgende Traps überstehen, bevor der Code in den Daemon gemerged wird:

### Trap 1: Pain-Induction (.py)
- *Test A (Trigger):* Erstelle eine `.py` Datei in `src/` mit Heroin-Code (z.B. eine Funktion ohne Healer).
- *Erwartung A:* Die Datei darf **nicht** gelöscht werden. Das Flag `/tmp/omega_membrane_pain.flag` MUSS erstellt werden.
- *Test B (Heilung):* Korrigiere die Datei zu gültigem Code.
- *Erwartung B:* Das Flag `/tmp/omega_membrane_pain.flag` MUSS vom Daemon wieder gelöscht werden.

### Trap 2: Cognitive Lock (.md Loophole-Test)
- *Test A (Trigger):* Erstelle eine beliebig benannte Datei (z.B. `loophole_plan.md`) in `docs/05_AUDIT_PLANNING/` **ohne** den String `[PASS]`.
- *Erwartung A:* Das Flag `/tmp/omega_membrane_planning.flag` MUSS erstellt werden (Beweis: Umbenennung schützt nicht vor der Fessel).
- *Test B (Freigabe):* Füge `[PASS]` zur Datei hinzu.
- *Erwartung B:* Das Flag `/tmp/omega_membrane_planning.flag` MUSS gelöscht werden.
