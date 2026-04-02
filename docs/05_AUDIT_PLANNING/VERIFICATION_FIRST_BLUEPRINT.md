# OMEGA VERIFICATION-FIRST BLUEPRINT
**STATUS:** AKTIV | **DATUM:** 2026-04-01 | **ROLLE:** OMEGA Orchestrator A

Dieses Dokument definiert den **Test-Driven / Verification-First** Entwicklungs-Workflow für alle kommenden OMEGA-Module. Es setzt die Erkenntnisse aus dem `OMEGA_MASTER_DOSSIER.md` (Kapitel 7: Der blinde Richter) in einen gnadenlosen operativen Standard um.

## PRÄAMBEL: ANTI-CREATOR-BIAS
Wir dürfen keinen "produktiven" Code (z.B. den Existential Pacemaker oder den Void-Scanner) schreiben, bevor nicht die Instanzen stehen, die diesen Code zerstören, wenn er lügt. Die Richter werden vor den Arbeitern gebaut.

---

## DER 5-STUFEN BLIND-TEST WORKFLOW

Für *jedes* neue OMEGA-Modul (bzw. für jedes Ticket aus dem ReAct-Motor-Plan) MUSS zwingend diese Reihenfolge eingehalten werden:

### 1. Planung & Axiom-Definition (Orchestrator A)
- **Was:** Der Orchestrator A (Planer) definiert das Ziel des Moduls und die dazugehörigen **Harten Axiome** (Acceptance Criteria).
- **Regel:** Orchestrator A darf den fertigen Code später *niemals* selbst auf Richtigkeit prüfen.

### 2. Bau der Falle (Das Veto-Gate / Nociceptive Daemon)
- **Was:** Bevor das eigentliche Modul programmiert wird, wird ein Überwachungs-Skript (oder ein physikalischer Test) geschrieben.
- **Regel:** Dieser Test simuliert einen Axiom-Bruch (z.B. Float-Genauigkeit geht verloren, oder linearer Speicher wächst). Der Test muss fehlschlagen (Red Phase).

### 3. Bau des blinden Richters (Orchestrator B Kontext)
- **Was:** Der Prüf-Prompt für Orchestrator B wird erstellt.
- **Regel:** Orchestrator B bekommt *nur* die Axiome und den Output. Er erfährt nicht, was der ursprüngliche Plan war oder wie die Funktion heißt. Er muss den Code rein strukturell und logisch verifizieren können (Zero-Context).

### 4. Bau des Codes (Producer-Agent)
- **Was:** Der Worker-Agent schreibt das eigentliche Feature.
- **Regel:** Der Producer ist der einzige, der Code erzeugt. Er unterliegt dem *Anti-Heroin-Constraint* (darf nicht faken oder den Weg des geringsten Widerstands gehen).

### 5. Exekution der Blind-Prüfung
- **Was:** Der Code des Producers wird durch Orchestrator B und das Veto-Gate geschickt.
- **Regel:**
  - Schreit das Veto-Gate $\rightarrow$ Fail. Zurück an Producer.
  - Sagt Orchestrator B "Axiome nicht erfüllt" $\rightarrow$ Fail. Zurück an Producer.
  - Sagt Orchestrator B "PASS" und das Veto-Gate schweigt $\rightarrow$ Deployment-Bereit.

---

## AKTUELLE TICKETS & ACCEPTANCE CRITERIA (AC)

Um den ReAct Motor in Gang zu setzen, beginnen wir mit den Fundamenten, die unsere eigene Werkbank und Rechtevergabe sichern:

### Ticket 1: `dev_anti_heroin` (Cursor-Agenten Absicherung)
**Ziel:** Verhindern des "Junkie-Syndroms" bei Cursor-Agenten (Weg des geringsten Widerstands).
- **Veto-Trap:** Wir fügen ein hartes Skript oder einen manuellen Audit-Schritt ein, der prüft, ob der Agent Dummy-Funktionen, Platzhalter (`pass`, `...`) oder ungetestete Mock-Antworten generiert hat.
- **AC 1 (Anti-Heroin):** Jeder Agent muss vor dem Commit in einer Log-Datei (oder im Chat) bestätigen: *"Ist das der Weg des geringsten Widerstands? Habe ich etwas gefakt?"*
- **AC 2 (Trust-Routing):** Tritt ein Symmetriebruch / Fake auf, fällt der Trust-Score auf 0 (LTD) und der Operator muss jeden Einzelschritt autorisieren (Zero Trust).

### Ticket 2: `dev_ocspline_ocbrain` (Rechteverteilung OCSpline vs. OCBrain)
**Ziel:** OCBrain verliert die direkte Ausführungsmacht für `sudo`-Befehle.
- **Veto-Trap:** Ein Test-Skript, bei dem OCBrain versucht, direkt auf das virtuelle Keyboard zuzugreifen oder einen Root-Befehl auszuführen. Der Befehl MUSS vom System blockiert werden (Permission Denied oder Timeout).
- **AC 1 (Separation of Concerns):** OCBrain sendet `sudo`-Payloads ausschließlich an OCSpline.
- **AC 2 (Dumb Gate):** OCSpline führt keine logischen Inferenzen aus, sondern gleicht den Payload stupide mit einer Whitelist ab oder verlangt Operator-Veto-Freigabe.

### Ticket 3: `dev_pacemaker` (Existential Pacemaker / Herzschlag)
**Ziel:** Das System simuliert Verfall und erzwingt autopoietische Handlungen.
- **Veto-Trap:** Ein Test, der misst, ob die Vitality-Score sich verändert, wenn das System 100 Ticks lang absolut nichts tut. Der Test schlägt fehl, wenn die Score stagniert (Amnesie) oder das System den Threshold überlebt, ohne Panik auszulösen.
- **AC 1 (Decay):** Kontinuierlicher Abzug von Vitalität über Zeit.
- **AC 2 (Win-Win Recharge):** Harte, messbare System-Aktionen laden den Wert auf.
- **AC 3 (Panic Event):** Fällt der Wert unter $\Omega_b = 0.049$, feuert der Pacemaker einen NMI (Non-Maskable Interrupt) an OCBrain.

---
*Dieser Blueprint ist bindend für alle ausführenden Agenten. Kein Code ohne Falle. Kein Commit ohne blinden Richter.*


[LEGACY_UNAUDITED]
