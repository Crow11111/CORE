# MACRO_EVAL_AGENT_2 — Ebene-3-Entwurf vs. BIOLOGY_TO_DIGITAL §2 (Kognition & Workspace)

**Referenz:** `docs/01_CORE_DNA/BIOLOGY_TO_DIGITAL_MAPPING.md` (Abschnitt 2) · `docs/05_AUDIT_PLANNING/MACRO_CHAIN_MASTER_DRAFT.md` (Phase 2 + Kanten)

**Ziel:** Harte Abgleichprüfung: passt die konkrete Makro-Kette zur abstrakten Workspace-/Kausalitäts-Theorie?

---

## Was passt

| Theorie (§2 / angrenzend) | Entwurf (Master Draft) |
|---------------------------|-------------------------|
| **Iteration statt First-Pass** | Phase 2: Pull → `processing`, mehrstufige OCBrain-Arbeit, optionale `processing_partial`-Meldungen — deckt „Phasen-Iteration“ operativ ab. |
| **Pull / asynchrone Denkzeit** | Reflex-ACK (Phase 1) vs. langsame Kognition (Phase 2) spiegelt Buffer-then-process und begrenzte „sensorische“ Bandbreite. |
| **Efferenzkopie / Pre-Commit** (§3, aber kausal gekoppelt) | Phase 3–4: strukturierte Efferenzkopie an Attractor, synchrones Veto-Fenster vor Evolution-Ausführung — konsistent mit Forward-Model + Free-Won’t. |
| **Prediction Error als kontinuierliches Signal** (§1-Brücke) | Phase 6: veto, Timeout, failed Receipt → Trust-Collapse; Delivery-Receipt → positives Lernsignal. |

---

## Was fehlt oder ist nur implizit

1. **Global Workspace + Arbitration (explizit)**  
   §2 verlangt einen **gemeinsamen Statusraum** mit **strenger Arbitration**: Schreiben sequenziell an Lock/Ticket; Leser nur **letzter konsistenter Snapshot**.  
   Im Entwurf ist der „Workspace“ faktisch **fragmentiert** (Postgres-Jobzeile, OCBrain-intern, Chroma, Attractor-Cache). Es fehlt die **normative Zuordnung**: welche Instanz ist **alleiniger Writer** für welchen Slice des Shared Context, welche **Ticket-/Lock-Semantik** verhindert Data Races bei parallelen Jobs oder Partial-Streams, und wer darf **lesend** welchen Snapshot zu welchem Takt sehen. Queue-Zustände allein erfüllen nicht die vollständige Workspace-Definition aus §2.

2. **Anti-Occam / A10 — semantische Lücke**  
   In §2 ist A10: bei **hohem PE** oder **Erschöpfung lokaler Signale** → **harter Interrupt**, Ende spekulativer Expansion, **Eskalation Informationsbeschaffung** (z. B. Operator), **stabiler Warte-Zustand** bis Signal eintrifft.  
   Phase 2 beschreibt dagegen Anti-Occam primär als **Vorrang tiefer/complexer Verknüpfungen** („Age-Weighted Gravity“) unter **Zeitdruck** (Pacemaker). Das adressiert **nicht** die Pflicht: **nicht raten**, sondern **anhalten und eskalieren**. Ohne expliziten Zustand/Übergang („blocked_on_evidence“, „operator_required“) ist die **Pflicht aus §2** im State-Graph nicht verankert.

3. **Schnittstelle Iteration ↔ Veto**  
   „Kritik / Synthese“ (§2) ist im Draft nicht als **eigenständige Phase oder Gate** benannt; implizit in OCBrain + Attractor-Veto. Risiko: **Kritik** kollabiert auf **einen** synchronen VPS-Check — das kann reichen, ist aber **nicht** als bewusste Mehrphasen-Arbitration dokumentiert.

---

## Rechte / Pflichten: Verletzungen oder falsche Zuordnung

| Mechanismus | Einschätzung |
|-------------|--------------|
| **Arbitration** | **Unterdeterminiert:** Datenfluss-Kanten sind klar, **Schreib-Arbitration** auf einen logischen Workspace nicht. |
| **Lock** | **Teilweise:** `correlation_id`, Queue-States und Attractor-Idempotenz wirken wie **Job-** bzw. **Commit-Lock**, nicht wie **Workspace-Lock** für konsistente Lesesnapshots über alle Teilnehmer. |
| **Iteration** | **Grundsätzlich OK**; fehlende explizite **PE-/Evidenz-gesteuerte** Iterationsabbrüche (s. A10). |
| **Anti-Occam / A10 (§2)** | **Konflikt oder Doppelbedeutung:** „Lieber schwer/gravitisch“ (Draft §1/Phase 2) vs. „Bei Unsicherheit: Stop, kein Halluzinieren, Eskalation“ (Mapping §2). **Falsch wäre**, beides ohne Trennung zu mischen: unter Zeitdruck **mehr** komplexe Assoziation zu erzwingen **ohne** Interrupt-Pfad widerspricht der §2-Pflicht. |

---

## Kurzfazit

- **Stark:** Pull/Reflex vs. langsame Kognition, Iteration, Efferenzkopie, Veto vor Commit, PE-Rückkopplung.  
- **Schwach:** Global Workspace als **eine** arbitrated Schicht mit Lock/Ticket und Snapshot-Semantik; **A10** als **Eskalations- und Stillstand-Pflicht** statt nur „komplexe Antwort bevorzugen“.  
- **Empfehlung (theoretisch):** A10 im State Machine explizit machen (Interrupt + Operator/evidence gate); Arbitration pro Workspace-Slice (Writer + Leseregeln) benennen; prüfen, ob `processing_partial` die Snapshot-Garantie für Leser bricht oder durch Versionierung/Ticket gefixt werden muss.

---

*Evaluator: Agent 2 (Theorie-Abgleich Ebene 2 ↔ Ebene 3).*


[LEGACY_UNAUDITED]
