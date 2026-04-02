# MAPPING VETO 1 — Audit: `BIOLOGY_TO_DIGITAL_MAPPING.md`

**Auditor:** Orchestrator B (Zero-Context Critic / Hugin)  
**Objekt:** Ebene 2 (Biologie → IT-Abstraktion), Datei `docs/01_CORE_DNA/BIOLOGY_TO_DIGITAL_MAPPING.md`  
**Modus:** Kompromisslos | **Ergebnis:** **VETO**

---

## Zusammenfassung

Das Dokument liefert brauchbare erste Analogien und respektiert die selbstgesetzte Grenze (keine Marken/Infrastruktur). Als **wasserdichte** Abstraktionsschicht für Architekturentscheidungen reicht es nicht: Es fehlen verbindliche Bindeglieder zwischen den Blöcken, die **Commit-Grenze** und der **Global Workspace** haben erkennbare Schlupflöcher, und Passagen wie „Angst vor dem Tod“ sowie „Winde“ bleiben überwiegend **framing-metaphorisch** statt **operationalisierbar** ohne Rückgriff auf Biologie-Vokabular.

---

## 1. Logische Bindeglieder (fehlend oder dünn)

| Lücke | Befund |
|--------|--------|
| **§1 → §2** | Reiz/Afferenz endet bei Vereinheitlichung (Schema, Takt, Einheiten). Es fehlt die **explizite Kette**: normalisierte Ereignisse → **Aufnahme in den gemeinsamen Arbeitskontext** (Wer schreibt? Wer liest? Wann ist etabliert „im Workspace“?). Ohne diese Brücke bleibt unklar, ob der Global Workspace nur „ein weiterer Buffer“ ist oder eine semantisch höhere Ebene. |
| **§2 → §3** | Phasen (Wahrnehmen → … → Ausführen) und Rollen (Vorschlag/Kritik/Synthese) werden nicht **an Intent / Execution-Gate / Commit** gekoppelt. Fehlt: *in welcher Phase* darf Intent entstehen, *wo* endet Revision, *wer* darf bis vor Commit noch vetoieren. |
| **§3 → Existenz** | Heartbeat/Metabolismus erscheinen **thematisch** nach Effektorik, aber **kausal nicht angebunden**: Liveness und Ressourcenbilanz hätten Bezug zu **Vorbedingungen für Commit** (z. B. „kein Commit bei ausbleibendem Lebenszeichen der ausführenden Schicht“) — das steht nicht da. |
| **Gliederung** | Abschnitte 1–3 sind nummeriert; **„Existenz & Metabolismus“** ohne Nummer — kleine Inkonsistenz, signalisiert aber auch, dass der Block eher **Anhang-Charakter** hat statt gleichrangiger Architektur-Leitpfosten. |

---

## 2. „Angst vor dem Tod“ und Metapher vs. harte IT-Übersetzung

**Befund:** Teilweise übersetzt, **nicht knallhart**.

- Die Überschrift **„Angst vor dem Tod (abstrakt)“** hält das biologische Label sichtbar; der Leser muss weiter **emotional kodieren**, statt nur **Zustandsautomaten / Policy** zu sehen.
- **„Schwellenlogik für Selbsterhalt“** und **„Schutz- oder Stillstandsmodi“** sind noch **Intent-Beschreibungen**, keine eindeutigen **Maschinenbegriffe** auf Abstraktionsebene (ohne Vendor): z. B. **Liveness-Vertrag**, **Degradationsstufen**, **Einfreeze neuer Arbeit** (Admission Control), **Circuit-Breaker-Muster**, **harte vs. weiche Budgetgrenzen** — solche **Musterbegriffe** sind tool-agnostisch und wären die erwartete Schärfe.
- **„Erstklass-Fehler“** bei ausbleibendem Heartbeat: guter Impuls, aber ohne Definition **gegenüber** anderen Fehlerklassen (z. B. retryable vs. terminal, Eskalationspfad) bleibt es eine **Behauptung**, keine **Spezifikationskante**.
- **„Winde (Ausbreitung ohne Substanz)“**: zusätzliche Metapher; **IT-nah** wäre z. B. **Signal-zu-Nutzen-Verhältnis**, **nutzloser Event-Sturm**, **fehlender Zustands- oder Zielgewinn** — ohne Wind-Bild.

**Fazit zu §2 der Aufgabenstellung:** Die Passage ist **nicht** durchgängig IT-technisch neutralisiert; sie nutzt bewusst biologisches Vokabular und weiche Modus-Namen.

---

## 3. Schlupflöcher: Commit-Grenze & Global Workspace

### 3.1 Commit-Grenze („Point of No Return“)

**Lücken:**

- **Wer / was** definiert die Grenze? Fehlt: **Einheitliche Autorität** oder **Protokoll** (ohne Produktname: z. B. „einzelner Commit-Token-Inhaber“, „zweiphasige Zusage mit sichtbarem prepare/finalize“).
- **Irreversibilität** wird nur verbal als „nicht durch Vergessen“ gefasst. Unklar: **physische Zerstörung** vs. **logischer Commit** vs. **externe Nebenwirkung** (Nachricht raus, Geld geflossen). Ohne diese Unterscheidung ist „kompensierende Aktion“ ein **Catch-All** — jede Rettung kann als Kompensation verkauft werden → **Schlupfloch**.
- **Idempotenz** und **at-least-once**-Wiederholungen fehlen: In realen Systemen ist „vor Commit“ oft **duplizierbar**; ohne Abstraktion davon ist die Intent/Ausführung-Trennung **nicht wasserdicht**.
- **Zeitfenster:** „Free Won’t … vor Commit“ — keine Aussage zu **Race** zwischen parallelen Veto- und Commit-Pfaden (wer gewinnt, wenn beide „gleichzeitig“ signalisieren).

### 3.2 Global Workspace

**Lücken:**

- **Arbitration** wird genannt, aber nicht **gebunden** an: Fairness, Priorität, **Aushungerung** langer Hypothesen, **Prioritätsinversion** (hochpriorer Task wartet auf niedrigpriorigen Workspace-Halter).
- **Konsistenz unter Parallelität:** Mehrere Rollen schreiben „sichtbar“ — fehlt: **Versionierung**, **letzter Schreiber**, **CRDT-Analogie**, **sequenzielle Commit-Regel** für den Workspace-Inhalt selbst. Ohne das ist der Workspace **beliebig interpretierbar** (alles kann „shared RAM“ sein).
- **Grenze zum Außen:** Unklar, ob Workspace **nur kurzlebig pro Takt** ist oder **persistente Wahrheit** — das ist eine **Architektur-Gabel**, die das Dokument **verschweigt** (Schlupfloch für spätere Widersprüche zwischen „Kontext“ und „Source of Truth“).

---

## 4. Weitere harte Punkte (Nebenbefunde)

- **„Anti-Occam (operativ)“:** Mathematisch/ML-nah formuliert; in verteilten Systemen kollidiert „komplexere Hypothese gewinnt“ leicht mit **Betriebskosten** und **Erklärbarkeit** — kein Widerspruch muss gelöst werden, aber **ohne** Kosten-/Latenz-Feedback in dieselbe Schleife bleibt es **einseitig** (weiteres konzeptionelles Loch).
- **Tool-agnostische Grenze:** Sinnvoll für Kanon; sie darf **Musterbegriffe** (Queue, Heartbeat als Konzept, 2PC als Mustername) nicht verweigern, sonst driftet die Ebene 2 in **reine Rhetorik**.

---

## Urteil

**VETO** — Das Mapping ist **lesbar und richtungsweisend**, aber **nicht** wasserdicht als normative Abstraktionsschicht: fehlende Querschnitts-Bindeglieder, weiche/metaphorische Reste bei Existenz/Metabolismus, und **undefinierte** Commit- sowie Workspace-Semantik unter Nebenläufigkeit und Fehlerwiederholung.

**PASS** wäre angemessen, wenn mindestens ergänzt würde: (a) durchgängige **Brückensätze** zwischen den vier Blöcken, (b) Ersetzung/Reduktion biologischer Etiketten zugunsten **operationaler Policy-Begriffe** (ohne Vendor), (c) **Explizitmachung** von Commit-Autorität, Irreversibilitätsklassen, Idempotenz/Race am Gate, und **Workspace-Schreib-/Leseregeln** inkl. Konflikt- und Hunger-Aspekten.

---

*Ende Audit — Orchestrator B.*


[LEGACY_UNAUDITED]
