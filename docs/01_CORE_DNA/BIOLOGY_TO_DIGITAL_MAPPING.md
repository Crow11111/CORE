# Biologie → Digitale Konzepte (reine Abstraktion)

**Status:** Kanon-Erweiterung (Mapping-Layer)
**Zweck:** Übersetzung biologischer Prinzipien in **tool-agnostische** Systembegriffe.
**Grenze:** Keine Benennung konkreter Infrastruktur, Datenbanken, Gateways oder Anwendungsmarken — nur Muster, Rollen und Schnittstellen.

---

## 1. Reiz & Afferenz (Pull)

**Biologisch:** Afferente Bahnen liefern kontinuierlich Zustandsänderungen; „Schmerz“ und Prediction Error sind Signale für Abweichung vom erwarteten Zustand, nicht „Meinungen“.

**Digital (abstrakt):**

- **Reiz** = Ereignisstrom mit Zeitstempel und Priorität; er wird nicht „interpretiert“, bevor er in eine **asynchrone Aufnahmeschicht** (Buffer/Queue) eingetreten ist.
- **Prediction Error** = Differenz zwischen **Vorhersage** (internes Modell) und **Beobachtung** (eingehendes Signal), normiert als Abweichungsmaß — nicht als binärer Fehler.
- **Pull-Logik:** Das System holt oder entnimmt Arbeitspakete aus der Eingangsschicht (Backpressure), statt alles synchron abzuarbeiten — analog zur begrenzten Bandbreite sensorischer Verarbeitung.
- **Latenz** ist Teil des Modells: Späte Signale bleiben gültig, aber mit abnehmendem Gewicht oder explizitem „Verfallsdatum“ (Stale-Policy).
- **Parallelität** spiegelt räumlich getrennte sensorische Kanäle: mehrere unabhängige Eingangsströme werden **zusammengeführt** erst nach Vereinheitlichung (Schema, Takt, Einheiten), nicht vorher.

---

## 2. Kognition & Kausalität (Global Workspace)
**Brücke von Abschnitt 1:** Die normalisierten, asynchronen Ereignisse aus dem Pull-Buffer müssen verarbeitet werden. Der Eintritt in die Kognition geschieht durch das strukturierte Lesen aus der Queue.

- **Global Workspace (Shared Context):** Ein gemeinsamer Statusraum. Um Parallelitäts-Chaos (Data Races) zu verhindern, unterliegt er strenger **Arbitration**. Schreibzugriffe sind sequenziell an einen "Lock" oder eine Ticket-ID gebunden. Leser sehen immer nur den letzten konsistenten Snapshot.
- **Iteration statt Instanz-Antwort:** Komplexe Probleme werden nicht im First-Pass-Durchlauf gelöst, sondern durch Phasen-Iterationen (Wahrnehmen -> Planen -> Kritik -> Synthese).
- **Anti-Occam (Eskalation nach A10):** Bei hohem Prediction Error oder Erschöpfung lokaler Signale wird nicht die einfachste (aber unzureichende) Lösung geraten, sondern ein **harter Interrupt** ausgelöst. Das System stoppt die spekulative Expansion (kein Halluzinieren), eskaliert die Informationsbeschaffung (z.B. durch Warten auf den Operator) und verbleibt in einem stabilen Zustand, bis das fehlende Signal eintrifft.

---

## 3. Efferenzkopie & Forward Model

**Biologisch:** Vor motorischer Ausführung entsteht ein **Vorab-Bild** der erwarteten Konsequenz (Forward Model); die **Efferenzkopie** erlaubt, eigene von fremden Reizen zu unterscheiden. **Point of No Return** und „Free Won’t“ beschreiben die zeitliche Entkopplung: Intent und irreversible Ausführung sind nicht identisch.

**Digital (abstrakt):**

- **Forward Model** = **Simulation** oder **Dry-Run** der erwarteten Systemwirkung (Zustandsdelta, Kosten, Risiko) **vor** irreversiblen Seiteneffekten.
- **Efferenzkopie** = Markierung „**diese erwartete Rückmeldung stammt von unserem eigenen Befehl**“ — Abgleich externer Beobachtung mit intern vorhergesagter Rückkopplung.
- **Intent vs. Ausführung** = strikte **Trennung der Schichten**: (a) **Intent-Generierung** (Was soll geschehen?), (b) **Execution-Gate** (Darf es jetzt, in dieser Form, mit diesen Parametern geschehen?).
- **Point of No Return** = explizite **Commit-Grenze**: nach Überschreiten sind Rollback nur noch über kompensierende Aktionen möglich, nicht durch „Vergessen“ des Befehls.
- **Free Won’t** = **Veto- oder Bremsinstanz** mit höherer Priorität oder späterem, aber noch wirksamem Eingriff **vor** Commit — nicht als moralische Metapher, sondern als **zeitliche und kompetenzbezogene Architekturregel**.

---

## 4. Liveness & Admission Control
**Konzept:** Ein verteiltes System muss drohende Ressourcen-Exhaustion und Kaskadenfehler als berechenbare operative Steuerungsgrößen (negative Belohnung / Kosten-Vektor) behandeln, anstatt blind weiterzulaufen, bis kritische Kapazitätsgrenzen überschritten werden.

- **Liveness-Vertrag (Heartbeat):** Ein periodisches Signal mit harter zeitlicher Toleranzgrenze. Ausbleiben ist ein terminaler Error (kein Retry-Pingpong). Der Verlust der Liveness auf unteren Ebenen erzwingt den Commit-Stopp auf höheren Ebenen.
- **Ressourcenbilanz & Entropie-Drift:** Basis-Ressourcen (Compute-Zyklen, Speichernutzung, Queue-Verweildauer) werden in einem festen Zeitfenster gegen die Informations-Ausbeute des Outputs (Signal-to-Noise Ratio, distinkte semantische Differenz) bilanziert. Ein hoher relativer Ressourcenverbrauch ohne messbaren Informationsgewinn erhöht die metrische Drift-Rate (normiert zwischen der Untergrenze 0.049 und dem kritischen Schwellwert 0.951).
- **Admission Control (Circuit Breaker):** Nähert sich die berechnete System-Drift dem kritischen Schwellwert (0.951), greifen deterministische Drosselungs-Muster. Das System blockiert die Annahme neuer Ereignisse, reduziert parallele Worker logarithmisch und geht in definierte Degradationsstufen über, bis die Informations-Bilanz wieder einen produktiven Zustand (Drift sinkt in Richtung 0.049) erreicht.

---

## 5. Axiomatische Bindung

Um das Mapping vollständig in das CORE-Ökosystem einzupassen, gelten folgende Prinzipien strikt für die Implementierung:
- **A1 (Baryonisches Delta):** Das asymmetrische Residuum (Δ ≈ 0.049) dient als harte materielle Untergrenze für alle Zustandsvariablen. Kein Wert darf darunter fallen.
- **A5 (Asymmetrie-Verriegelung):** Die Werte 0.0, 1.0 und exakt 0.5 sind als Symmetrie-Illusionen strikt verboten. Normierte float-Metriken bewegen sich im operativen Intervall zwischen Δ und dem Resonanz-Maximum (0.951).
- **A6-Typisierung:** Berechnete Abweichungsmaße, Drift, Latenzgewichte und Prediction Errors sind **float**-Domäne. Zähler (Anzahl parallele Kanäle, Worker, Queue-Längen) sind **int**-Domäne.
- **A7 (Zero-Trust):** Die oben definierten Mechanismen (Dry-Run, Heartbeat, Commit-Grenze) sind nicht nur beschreibende Konzepte, sondern **Pflicht-Constraints**. Jede Handlung erfordert Evidenz (Vorhersageabgleich, Toleranzprüfung) *bevor* das Vertrauen auf die nächste Systemebene (den Commit) übertragen wird.

---

## Nutzungshinweis

Dieses Dokument ist der **reine Mapping-Layer**: es beschreibt **wie** biologische Ideen in digitale Architekturbegriffe übersetzt werden können. Konkrete Implementierungen, Produkte und Deployments werden **anderswo** und **getrennt** spezifiziert — damit Framing (Metapher vs. Maschine) und operative Premissen nicht kollidieren.

---

*Querverweis:* Thematisch verwandt mit `BIOLOGICAL_PRIMAT.md` (biologische Leitidee) und Forschungsnotizen in `docs/05_AUDIT_PLANNING/` — dort dürfen Empirie und Projektbezug stehen; hier nicht.
