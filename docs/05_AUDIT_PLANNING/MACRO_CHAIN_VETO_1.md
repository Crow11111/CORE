# MACRO-CHAIN — VETO-AUDIT (Orchestrator B / Hugin)

**Gegenstand:** `MACRO_CHAIN_MASTER_DRAFT.md`  
**Modus:** Zero-Context Critic (kein Mitleid mit Metaphern — nur schließbare Kausalität)  
**Datum:** 2026-04-01  

---

## Gesamturteil: **VETO**

Der Draft ist als **narrative Synthese** brauchbar; als **operatives Kausalitäts- und Timing-Modell** ist er **nicht abnahmefähig**. Es fehlen schließbare Rückkopplungs- und Durchsetzungspfad-Spezifikationen. Die folgenden Punkte blockieren PASS.

---

## 1. Timing (Asynchronität, Parallelität, Flaschenhälse)

### Was stimmig ist
- **Afferenz vs. Workspace:** Die Zuordnung „parallel / latenzbehaftet“ (Eingang) vs. „sequenziell / zeitintensiv“ (OCBrain) entspricht dem skizzierten biologischen Bild.
- **Schmales Veto-Fenster:** Spätes, kurzes Gate nach langem RP-Aufbau ist mit dem Draft konsistent.

### VETO-Gründe
1. **„Massiv parallel“ ist nur auf Request-Ebene wahr.** Pro einzelner Kausal-Kette (eine User-Nachricht → eine Antwort) bleibt der Einstieg typischerweise **Kong → Spline → Queue**: ein **serieller Front-Door**, nicht ein neurologisch verteilter Bus. Der Text suggeriert stärkere innere Parallelität, als im Modell abgebildet ist.
2. **Phase 2 behauptet „Phasenverschränkung“ und „mehrere parallele Denkpfade“, ohne Bindung an einen Scheduler.** Wer serialisiert Ergebnisse? Wer definiert „zusammengeführt“ vor Efferenzkopie? Ohne **Merge-/Arbitration-Regel** ist das Timing der Kognition formal unterbestimmt.
3. **Sofortiges `200 OK` (Phase 1) vs. Nutzer-Erwartung:** Biologisch ist das ein peripherer Reflex; kognitiv entsteht beim Nutzer sofort ein **Erwartungs-Zeitfenster** für Inhalt. Der Draft verbindet **ACK-Latenz** nicht mit **Antwort-Latenz** oder mit einer definierten **Zustandsmaschine** (z. B. „queued / processing / vetoed / sent“), die Prediction Errors auf UI/Protokoll-Ebene begrenzt.
4. **„100 ms bis Minuten“ für Phase 2:** Die untere Grenze ist wohl optimistisch, sobald Chroma/Monica und mehrstufige Agent-Tasks dazukommen. Ohne **SLA pro Subschritt** bleibt „Expected Arrival“ (Abschnitt 3.3) eine Phrase ohne Messgröße.

---

## 2. Gewaltenteilung (VPS-Veto, Efferenzkopie, Spline als Thalamus/Motorcortex)

### Was stimmig ist
- **Veto auf dem VPS „direkt vor dem Ausgang“** ist als politische Forderung klar und mit der Korrektur in Abschnitt 3.2 konsistent.
- **Spline = Thalamus (Ein) + Motorcortex (Aus)** ist im Dokument explizit; die Rollentrennung zu OCBrain („rein kortikal“) ist nachvollziehbar.
- **Efferenzkopie vor Außenwelt:** Die Reihenfolge „Entwurf → Veto → Ausführung“ ist logisch.

### VETO-Gründe
1. **Topologie-Lücke:** Der Draft sagt nicht, **auf welchem Host** OCSpline läuft und wie der **Pfad** „Firewall pass → Spline → Evolution“ technisch aussieht (interner Call, Queue, Rückweg über Dreadnought?). Wenn der „Muskel“ nicht **topologisch hinter** dem gleichen Veto-Egress hängt, ist die Metapher **hohl** und das Sicherheitsargument **angreifbar**.
2. **Durchsetzung fehlt:** „Kein direkter API-Call von OpenClaw zu Evolution“ (Abschnitt 4) ist eine **Policy**, keine **Architektur**, solange nicht spezifiziert ist: Netzwerk (Firewall-Regeln), Credentials (nur Attractor/Spline), Code-Pfad-Audit, **Idempotenz-Keys** gegen Doppel-Send. Ohne das ist „MUSS“ nur Dokumentation.
3. **Anti-Heroin-Validator neben Firewall:** Benennt, aber nicht **wo** im Millisekunden-Fenster er läuft (sync blockierend? async mit Pre-Veto?). Risiko: Veto-Fenster wird zur **Fassade**, wenn teure Checks ausgelagert oder umgangen werden.
4. **Efferenzkopie als Objekt:** Kein Wort zu **Schema**, **Korrelation-ID**, **Replay-Schutz**, **Versionierung**. Ohne das kann die Efferenzkopie weder verifiziert noch forensisch an die Queue gekoppelt werden.

---

## 3. Kausalitätskette — Prediction Error & Rückmeldung

### Was stimmig ist
- **Libet/Veto** und **Forward Model** sind sauber als Analogien eingeführt.
- **Veto → „Schmerz-Signal an Queue“** ist eine rudimentäre negative Rückkopplung.

### VETO-Gründe (kritisch)
1. **Abschnitt 3.3 behauptet Lernen aus „Latenz-Drifts“ wie aus Prediction Errors — ohne geschlossenen Kreis.** Es fehlt:
   - **Wer** berechnet den Fehler (Δ zwischen erwarteter und tatsächlicher Ankunft)?
   - **Welches Signal** (Skalar, Event, strukturierter Record) geht wohin?
   - **Wer** aktualisiert Policy/Gewichte/Timeouts — OCBrain, separates Modul, Queue-Consumer?
   Ohne diese drei Antworten ist „lernt aus Prediction Errors“ **nicht falsifizierbar** → Anti-Heroin-Verdacht: narrative Beruhigung.
2. **Positive Vorhersage vs. Outcome:** Biologische PE vergleicht **Vorhersage mit Sensorik**. Im Draft gibt es keine **explizite** Stufe „vorhergesagte Antwort / tatsächliche Kanal-Rückmeldung“ (z. B. Evolution-Delivery-Receipt, Fehlercode). Veto ist binär; **graded PE** für Feintuning fehlt.
3. **„Schmerz-Signal an Queue“:** Unklar, ob dasselbe Item **requeued**, ein **neues** Toxic-Event ist, oder OCBrain **benachrichtigt** wird. Ohne Semantik droht **Endlosschleife** oder **stilles Verschlucken**.

---

## 4. Mindestliste für PASS (ohne Implementierung — nur Spezifikation)

1. **Eine Sequenzdiagramm-pflichtige Kette:** Host-Grenzen + ein erlaubter Datenfluss von Afferenz bis Efferenz (inkl. Veto-Pass).
2. **Efferenzkopie-Kontrakt:** Pflichtfelder, IDs, Ablauf, was bei Partial-Output passiert.
3. **Prediction-Error-Pfad:** Produzent, Konsument, Speicherort, Trigger (Latenz, Veto, Delivery-Failure), keine bloße Analogie.
4. **Bypass-Verhinderung:** Technische, nicht nur textliche Absicherung des OpenClaw→Evolution-Verbots.
5. **Phase-2-Merge:** Regel, wie parallele Denkpfade vor der Efferenzkopie zu **einem** handlungsfähigen Entwurf werden.

---

## Kurzfassung für Ring 0

| Dimension        | Bewertung |
|------------------|-----------|
| Timing-Story     | plausibel, aber Front-Door/Parallelität und Merge fehlen |
| Gewaltenteilung  | intent klar, Topologie + Enforcement offen |
| PE / Rückkopplung| **Lücke** — zentraler Blocker |

**Signatur:** Orchestrator B (Hugin) — **VETO**


[LEGACY_UNAUDITED]
