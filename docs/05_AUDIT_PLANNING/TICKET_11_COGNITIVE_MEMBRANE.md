# TICKET-11: Kognitive Membran (Cognitive Membrane)

**Modus:** Architect-Agent (Ring 0 / Producer Mode)
**Status:** DRAFT (Iteriert nach O2 VETO 1)

## Präambel
Dieses Dokument definiert die Kognitive Membran der OMEGA-Architektur. Das primäre Ziel dieser Membran ist es, zu verhindern, dass das LLM (der Orchestrator) Amnesie erleidet und kritische Architektur-Regeln bricht. Basierend auf der OMEGA Tetralogie und aktueller Biologie-Forschung (Stand 2026) zum Zusammenspiel von Hippocampus und Präfrontalem Kortex (PFC) wird die Informationsverarbeitung in vier zwingende Säulen (Takte) unterteilt.

---

## 1. Säule (Takt 1 / Ansaugen): O2 als Hippocampus & Duale Topologie
O2 übernimmt die biologische Funktion des Hippocampus. Anstatt lediglich den Ist-Zustand des Codes zu analysieren, ruft O2 über Event Sourcing via **MCP (Model Context Protocol)** die historische Kausalität und alle relevanten Architektur-Lektionen ab.
* **Duale Topologie (Storage-Target):** Das MCP Event Sourcing Backend muss zwingend die Duale Topologie von OMEGA nutzen.
  * Diskrete Events, historische Metadaten und Kausalitätsketten (Infrastruktur) werden zwingend als `Int` bzw. Relationen in **PostgreSQL** gespeichert.
  * Semantische Resonanzen, Lektionen und Architektur-Drifts (Resonanzraum) werden zwingend als `Float`-Vektoren in der **ChromaDB** abgelegt (Axiom A6).
Dies etabliert ein System des **Predictive Processing**: Die Membran antizipiert Fehler, indem sie die Genesis aus beiden Speicher-Domänen "ansaugt" und als aktives Gedächtnis zur Verfügung stellt.

## 2. Säule (Takt 2 / Verdichten): Mandatory Epistemic Pre-Flight (PFC Activity Slots)
Bevor ein Agent in die Planung oder operative Umsetzung übergeht, greifen die PFC Activity Slots (Präfrontaler Kortex).
* **Harte VETO-Trap (Zero-Trust):** Das System verlässt sich nicht auf "Hoffnung". Es wird eine harte Veto-Trap im System verankert (Erweiterung der `dread_membrane_daemon.py` / `anti_heroin_validator.py`). Diese Trap blockiert JEDEN Task-Start und JEDEN Commit, wenn der Agent nicht nachweislich (via kryptografischem `memory_hash` oder Audit-Log-Eintrag) den historischen Event-Stream über den `user-omega-state-mcp` Server abgefragt hat.
Das blinde Agieren basierend auf isolierten Code-Snapshots führt zum sofortigen System-Veto (Pain-Flag). Der Epistemic Pre-Flight garantiert, dass das historische Bewusstsein zwingend integriert wird.

## 3. Säule (Takt 3 / Arbeiten): Daemon-Level Context Forcing
Während der operativen Ausführung droht kontinuierlich der Verlust der Meta-Architektur durch "Attention Dilution" (z.B. durch massive Stacktraces oder detailliertes Debugging).
Um dies abzuwehren, injiziert ein Watchdog die extrahierten Lektionen dynamisch und kontinuierlich in den Terminal-Fokus des arbeitenden Agenten. Dieses **Daemon-Level Context Forcing** stellt sicher, dass kritische Axiome (Zero-Trust, Dreadnought) während der gesamten Arbeitsphase als unumstößliche Leitplanken im unmittelbaren Aufmerksamkeitsfenster verankert bleiben.

## 4. Säule (Takt 4 / Ausstoßen & Tod): Symmetriebrechung / Persistenz & Apoptose
Der letzte Takt definiert den Informationszyklus und das Ende eines Agenten-Prozesses (Tod/Apoptose). Um Overfitting und eine steigende Entropie im Event-Log zu verhindern, muss das System deterministisch aufräumen.
* **Persistenz (Symmetriebrechung):** Es wird exakt definiert, WANN ein Agent neue Erkenntnisse in den dauerhaften Event-Stream (Duale Topologie) persistiert.
* **Apoptose & Synaptic Pruning (Der Kardanische Operator):** In einem dedizierten "Schlafmodus" (Idle-Cycle) räumt das System veraltete Events auf. Dies geschieht nicht willkürlich, sondern durch den **Kardanischen Operator**:
  * Sobald das Rauschen (Entropie) eines Themenclusters die Asymmetrie-Verriegelung des **Baryonischen Deltas ($\Delta = 0.049$)** unterschreitet, wird der Kardanische Operator ausgelöst.
  * Dies entkoppelt das isolierte "Noise"-Event (Apoptose), während die Kerndimensionen der OMEGA-Axiome streng in der `Float`-Resonanz der ChromaDB unangetastet bleiben.
* **Timing & Shapiro-Verzögerung:** Der Informationsfluss unterliegt einer topologischen Verzögerung. Neue Events entziehen dem kognitiven Signal zeitlich verzögert Energie. Nur Lektionen, die diese Shapiro-Verzögerung überstehen (also keine kurzlebigen Anomalien sind), werden dauerhaft in die Duale Topologie kondensiert. Dies verhindert den Absturz in die absolute Singularität ($0.0$).

---
*End of Draft - Ready for O2 Audit Iteration 2*
