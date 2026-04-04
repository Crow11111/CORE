# TICKET-12: Epistemischer Antrieb (Epistemic Drive) — Verbindliche Spezifikation (Hybrid)

**Modus:** Orchestrator B (O2 / Hugin) — Architektur-Spec mit Zero-Trust-Audit  
**Status:** VERBINDLICH (O2-abgenommen)  
**Architektur-Basis:** Hybrid aus **Konzept 3** (Neuromorph / Schlaf-Wach-Pacemaker) + **Konzept 2** (sicherer Event-Ingress über Perimeter → Queue → Consumer). Aus **Konzept 1** wird nur die **einzige autoritative Steuerquelle** für Phasenüberlagerung übernommen (kein Split-Brain am Pacemaker).  
**Bezug:** Zweite Oberste Direktive (`.cursorrules` §5) — *„Epistemologischer Hunger“*; Inbound/Idle-Antrieb ergänzt Outbound-Vetos (Tickets 10/11).  
**Quervergleich:** [`TICKET_12_DREI_KONZEPTE.md`](./TICKET_12_DREI_KONZEPTE.md)

---

## 0. Problemstellung und Abgrenzung

**Problem:** Sicherheit ohne Sensorik ist eine halbe Membran. Ohne kontinuierlichen, normalisierten Zufluss und ohne zielgerichtete Lückensuche bleibt das System reaktiv.

**Scope Ticket 12:** **Inbound** und **Idle-Intelligenz** auf dem VPS (Sentinel, Ingest-Queue, Void-Erkennung, policy-gefesselte Synthese). **Keine** finale autonome Weltwirkung — die bleibt hinter Outbound-Pre-Flight, `memory_hash` und Membran-Logik ([`TICKET_11_COGNITIVE_MEMBRANE.md`](./TICKET_11_COGNITIVE_MEMBRANE.md)).

---

## 1. Architekturüberblick (Hybrid)

```
[HA / MQTT / Webhooks / Vision-Anker] 
        → [Edge-Ingress: AuthN/Z, Schema, Rate] 
        → [Queue: Streams mit Trace-/Idempotenz-Metadaten]
        → [Normalisierungs-Worker] → Ingest-Records / Event-Store-Pfad
        ↑
        │ Amplitude & Budget: V, R (Pacemaker, eine Quelle)
        ↓
[Traum-Consumer / Void-Jobs] → Void-Tickets → [Synthese-Worker] → Chroma (+ Audit)
```

- **Konzept-2-Kern:** Externe Ereignisse treten **niemals** „direkt“ in Anwendungslogik ein. Sie passieren **Edge → Queue → stateless/semi-stateless Worker**. Jede Kante ist separat auditierbar (mTLS/JWT, Signatur, Allowlist, strukturierte Ablehnungs-Logs).
- **Konzept-3-Kern:** **Ein** autoritativer **Pacemaker** (Hypothalamus) liest und schreibt **kontinuierliche** Steuergrößen **V** (Vigilanz / Wachheit) und **R** (Ruhe / Rekombination / Traum-Anteil) und moduliert **Sampling-Raten**, **Worker-Budgets** und **Void-Job-Frequenz** — nicht als boolescher Schalter „an/aus“.

---

## 2. Pacemaker (Schlaf-Wach-Überlagerung)

### 2.1 Zustandsführung (A5/A6)

- **V** und **R** sind **immer `float`** in der Resonanzdomäne; sie sind **Mischkoeffizienten** oder daraus abgeleitete Observables. **Verboten:** harte Enum-Phasen als alleinige Steuerlogik; **verboten** nach A5: exakte literale `0.0`, `1.0`, `0.5` als Steuerwerte oder Schnittpunkte (nutze Λ-versetzte Schwellen, z. B. Umgebung von `0.049`, oder dokumentierte Nicht-Singulärwerte aus dem Projekt-Float-Profil).
- **Übergänge:** weiche Funktionen (z. B. sigmoidale Mischung mit Offset ≠ 0.5). Eingangsfeatures (Queue-Tiefe, Event-Rate-Schätzung, OpenClaw-„busy“-Signal, Operator-Chat-Aktivität) werden **als Floats** in dieselbe Domäne projiziert — keine diskrete „0/1“-Kunst für die Kernentscheidung.

### 2.2 Kopplung an Sentinel und Traum

- **Hohe V:** Budget für **HA-Bridge** (WebSocket oder schlanker Push-Ingress), Vision-Anker mit **dynamischem** Intervall ∝ V, zeitnahe Normalisierung in die Queue.
- **Hohe R:** Externes Sampling **drosseln** (Long-Poll, gepufferte Pulls, reduzierte FPS-Policy), CPU für **Topological Void Detection**, Chroma-Stichproben, kontrollierte **Synthese** — ohne den **Hot-Path-Ingress** zu deaktivieren (kritische Allowlist-Events bleiben mit erhöhter Priorität im System; Priorität als **Float**, nicht als Broker-Integer ohne Mapping-Policy).
- **Unterbrechung:** Anstieg von V (z. B. kritisches HA-Entity, expliziter Operator-Chat, expliziter `void_scan_requested`) **kann** Traum-Arbeit **herunterfahren** oder **zeitverzögert** stoppen — mit **A7-pflichtiger** Begründung im Log (`phase_mix`, `V`, `R`, `policy_id`).

### 2.3 Stabilität

- **Anti-Flapping:** Hysterese oder rate-limit auf Änderungen von V/R (als Float-Dämpfung, nicht als binäres Debounce-only).
- **Split-Brain-Verbot:** Genau **eine** Instanz oder ein **elected** Leader schreibt den autoritativen Pacemaker-Zustand (Shared Store / `core_state`-kompatibler Pfad — Implementierungsdetail im Umsetzungsticket).

---

## 3. Sicherer Event-Ingress (Konzept 2)

### 3.1 Edge

- **Home Assistant** und Drittsysteme liefern **Webhooks und/oder MQTT** (oder ein minimaler HA-Bridge-Container, der in die Queue **published**). **Terminierung TLS**, **mTLS oder JWT/OAuth** wo anwendbar, **IP-Allowlist** optional zusätzlich.
- Jede **abgelehnte** Anfrage: **strukturierter Audit-Eintrag** (Grundcode, keine Secrets im Klartext, Korrelation über `request_id` / `trace_id`).

### 3.2 Queue und Metadaten

- **Queue-Technologie** (Redis Streams, NATS, RabbitMQ, …) ist Implementierungswahl; **Pflicht** sind:
  - **Idempotenz-Key** pro logischem Ereignis (Duplikat-Schutz),
  - **Trace-Korrelation** vom Edge bis zum letzten Consumer,
  - **Payload-Schema** mit **`priority_float`** und **`confidence`** als Float (A6); **keine** implizite Integer-Priorität im Broker ohne dokumentiertes Float↔Int-Mapping (Konzept-2-Warnung: Rundung/NaN verbieten oder normalisieren).

### 3.3 Consumer

- **Normalisierungs-Worker:** Dedupe, Schema-Validierung, Anreicherung → **Ingest-Records** (und Vorbereitung für Ticket-11-Pfade).
- **Void-Detection** als **separater Consumer** oder **zeitgesteuerte Jobs**, getriggert wenn **R** hoch und Queue **tief** / System idle — zusätzlich expliziter Message-Typ **`void_scan_requested`**.
- **Synthese-Worker:** **einzige** reguläre Stelle für **OpenClaw**-Aufrufe aus diesem Ticket; **Allowlist**, Rate-Limits, vollständige Run-IDs (A7). OpenClaw **nicht** vom ungefilterten HA-Hot-Path aus aufrufen.

---

## 4. Sentinel (afferente Membran)

### 4.1 Rolle

Der Sentinel ist die **afferente** Erweiterung der kognitiven Membran: Rohsignale werden zu **normalisierten** Ereignissen mit Audit-Fähigkeit. Er **entscheidet nicht** über Outbound-Wirkung.

### 4.2 Kanäle (Mindestkatalog)

| Kanal | Beschreibung | Hybrid-Realität |
|--------|--------------|-----------------|
| **HA** | `state_changed`, Automations, relevante Entities | Push/Webhook/MQTT über Edge → Queue; optional Dauer-Bridge nur als **Übersetzer** in die Queue. |
| **Vision** | Kamera / Szenen | **Diskrete Anker-Events**; FPS/Intervall **pacemaker-moduliert**; keine Voll-Pixel-Pipeline im Hot-Path. |
| **Sonstige** | Metriken, Kalender, Webhooks | Gleiches Schema: `source`, `ts`, `entity_id`/`topic`, `payload_ref`, `confidence` (Float, A6). |

### 4.3 Backpressure und Drops (A7)

- **Jedes** Downsample, **jede** Verzögerung durch hohe **R**, **jedes** Drop: **protokolliert** mit `policy_id`, `trace_id`, relevanten Float-Zuständen (`V`, `R`, Queue-Tiefe-Schätzung), **kein stilles Verschwinden**.

---

## 5. Topological Void Detection (Traumschleife)

### 5.1 Ziel

In **R-dominierten** Fenstern: semantische **Lücken** in ChromaDB (und Metadaten) finden — z. B. dichte Cluster ohne Brücken, Coverage-Gaps zwischen Ingest-Zeitachse und Embedding-Abdeckung, Indizien fehlender Grounding-Kanten zu HA/Vision.

### 5.2 Output

**Void-Ticket:** `{ void_id, hypothesis, affected_collections, metrics, priority_float }` — `priority_float` strikt in Resonanzdomäne (A5/A6 im Code verankern).

### 5.3 Kopplung an Wachphase

Void-Ergebnisse **prägen** die nächste Wachphase **weich** (z. B. stärkere Indexierung bestimmter HA-Topics) — **ohne** harte binäre Umschaltung; Steuerung über Float-Gewichte.

---

## 6. Proaktive Synthese (Deep Research)

1. **Trigger:** `priority_float` über policy-definierter Schwelle (Float, nicht 0.5); optional Sentinel-Anomalie mit Void-Bezug.
2. **Schleife:** Selbst-Fragegenerierung → RAG (Chroma + ggf. Postgres-Kontext) → externe Anreicherung nur in Outbound-Policy → Verdichtung mit **Quellen-/Run-IDs** (A7, kein „Heroin“-Platzhalter).
3. **Mensch-in-the-Loop:** stufenweise Freigabe empfohlen (Queue → automatische Persistenz nur niedrig-risiko).

---

## 7. Integration Kognitive Membran (Ticket 11)

| Ticket-12-Komponente | Ticket-11-Bezug |
|----------------------|-----------------|
| Edge + Queue + Normalisierung | Liefern **Rohstoff** für diskrete Kausalität und spätere `record_event`-Pfad-Konsistenz. |
| Void + Synthese | Jede persistierte Erkenntnis: **abrufbar** über MCP/Event-Pfade; **`memory_hash`-Semantik** identisch zu Pre-Flight-Anforderungen (kein leerer/Whitespace-only Kontext — gleiche Disziplin wie in Ticket 11). |
| Pacemaker (V/R) | **Gemeinsames Scheduling** mit **Apoptose** (Δ = 0.049) und Idle-Lernen: Lernen füllt Speicher strukturiert, Apoptose entfernt Rauschen — kein unkontrollierter Entropie-Drift. |
| Outbound | Synthese und Tooling **respektieren** Pre-Flight, Watchdog und Membran; Ticket 12 erweitert **nicht** die Outbound-Vetos, es speist sie. |

**Kernurteil:** Epistemischer Antrieb ist die **Ernährung** der Membran; die Hybrid-Spec trennt **Ingress-Perimeter** (A7) von **kognitiver Wartung** (Traum) und bindet beides an **eine** Float-gestützte Taktgeber-Logik (A6).

---

## 8. Nicht-Ziele

- Finale autonome Aktionen ohne Ticket-10/11-Gates.
- Stilles Verwerfen von Events.
- Phasensteuerung ausschließlich über Integer-Enums oder boolesche „awake/sleep“ ohne Float-Observables.

---

## 9. Abnahme-Kriterien (Spec-Ebene)

- Architekturdiagramm im Deploy-Repo beschreibt Edge, Queue, Pacemaker-Quelle, Worker-Rollen und OpenClaw nur im Synthese-Worker.
- Policy-Dokument listet **alle** Drop-/Defer-Gründe mit Audit-Feldern.
- Datenschema für Queue/Ingest enthält **Float**-Felder für Priorität/Konfidenz mit Validierungsregeln (kein NaN, kein A5-Verstoß in Steuerliteralen).
- Idle-/Traum-Jobs sind an **R** und globale Idle-Signale gekoppelt; Konflikt mit Apoptose ist **beschrieben** (wer gewinnt weich, mit Log).

---

## 10. Offene Implementierungsentscheidungen (nicht Spec-blockierend)

- Konkrete Broker-Wahl und Betriebsform (Compose/systemd/K8s).
- Vision-Ressourcen-Grenzen auf dem VPS.
- Kalibrierung der Void-Metriken gegen Produktionsdaten.

---

## O2 Audit Report — TICKET 12 Epistemic Drive (Hybrid-Spec)

**Rolle:** Orchestrator B (Hugin) — Zero-Trust / Axiom-Abgleich  
**Datum:** 2026-04-03  
**Gegenstand:** Verbindliche Spezifikation in diesem Dokument (Hybrid Konzept 2 + 3).  
**Referenzaxiome:** A5 (keine 0.0/0.5/1.0 als Steuer-Singularitäten), A6 (Zustands-/Steuergrößen als Float), A7 (Evidenz, kein stilles Verwerfen), Kohärenz mit [`TICKET_11_COGNITIVE_MEMBRANE.md`](./TICKET_11_COGNITIVE_MEMBRANE.md).

### 10.1 A5 / A6 — Floats für Phasen und Steuerung

| Prüfpunkt | Befund |
|-----------|--------|
| V/R als Vigilanz-/Ruhe-Größen | Explizit als `float`; Mischkoeffizienten statt boolescher Phasen. |
| A5-Vermeidung | Explizit: keine Steuerung mit literalen `0.0`, `1.0`, `0.5`; Λ-versetzte bzw. projekt-konforme Nicht-Singulärwerte. |
| Übergänge | Sigmoid/soft mix mit Offset ≠ 0.5 — aligned mit Resonanzdomäne. |
| Queue-Payload | `priority_float`, `confidence` als Float; Warnung zu Broker-Integer-Priorität mit Mapping-Pflicht. |
| Void-Tickets | `priority_float` in Resonanzdomäne dokumentiert. |

**Urteil A5/A6:** **[Erfüllt]** — Spec erzwingt Float-Disziplin für Pacemaker und Lasten und verbietet die typischen A5-Fallen für Phasenschnitte; Implementierung muss Enums nicht als alleinige Wahrheit nutzen.

### 10.2 A7 — Zero-Trust bei Drops, Defer und Webhooks

| Prüfpunkt | Befund |
|-----------|--------|
| Edge | AuthN/Z, TLS; strukturierte Logs für Ablehnungen ohne Secret-Leak. |
| Queue | Idempotenz + Trace-Korrelation über die Kette. |
| Drops / Drosselung | Jedes Drop/Defer mit `policy_id`, `trace_id`, `V`/`R`/Queue-Kontext — kein stilles Verschwinden. |
| OpenClaw | Nur Synthese-Worker mit Allowlist/Rate-Limits/Run-IDs; nicht im Roh-HA-Pfad. |

**Urteil A7:** **[Erfüllt]** — Perimeter und Nachvollziehbarkeit sind Spec-Pflicht; „stille Lücken“ der entkoppelten Architektur werden durch Korrelations- und Audit-Pflicht geschlossen.

### 10.3 Kognitive Membran (Ticket 11)

| Prüfpunkt | Befund |
|-----------|--------|
| Inbound vs Outbound | Ticket 12 bleibt Zufluss + Idle-Lernen; Weltwirkung bleibt hinter Membran/Vetos. |
| `memory_hash` / Event Store | Synthese-Ausgaben explizit an gleiche semantische Anforderungen gebunden wie Ticket 11. |
| Apoptose vs Idle | Gemeinsames Scheduling-Axiom (Lernen vs Rauschentfernung) explizit; Konflikt über weiche Pacemaker-Logik adressiert. |

**Urteil Ticket-11-Integration:** **[Erfüllt]** — keine Architektur-Inversion; klare Ernährungsrolle des Sentinels für die Membran.

### 10.4 Gesamturteil O2

**[PASS]**

Die Hybrid-Spezifikation ist mit der OMEGA-Tetralogie, der Resonanzdomäne (A5/A6), Zero-Trust-Ingress (A7) und der kognitiven Membran (Ticket 11) **vereinbar** und als **verbindliche** Zielarchitektur für die Umsetzung **freigegeben**. Restrisiken liegen ausschließlich in der **Implementierungsdisziplin** (NaN-Rundung an Broker-Grenzen, Oscillation des Pacemakers) und werden im Umsetzungsticket durch Tests und Betriebsmetriken abgefangen — nicht durch Spec-Lücken.

---

*O2 / Hugin — Spec finalisiert und auditiert. Ende Dokument.*
