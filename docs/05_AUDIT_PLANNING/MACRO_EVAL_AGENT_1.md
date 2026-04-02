# MACRO-CHAIN vs. BIOLOGY_TO_DIGITAL_MAPPING — Evaluierung (Agent 1)

**Gegenstand:** Abgleich `MACRO_CHAIN_MASTER_DRAFT.md` (§2 Topologie, §3 Phase 1) mit `BIOLOGY_TO_DIGITAL_MAPPING.md` (§1 Reiz & Afferenz).  
**Fragestellung:** Passt Ebene 3 (konkreter Entwurf) zu Ebene 2 (abstrakte Afferenz-Theorie)? Wo fehlen Pflichten / wo sind Push/Pull, Latenz und Vereinheitlichung falsch oder unklar zugeordnet?

---

## Was passt

| Theorie (§1) | Entwurf |
|--------------|---------|
| Reiz zuerst in eine **asynchrone Aufnahmeschicht**, nicht vorher „interpretiert“ | **Thalamus-Gate:** Job landet als `queued` in Postgres mit `correlation_id`; Kognition (OpenClaw) erst danach. |
| **Pull** der Arbeit aus der Eingangsschicht (begrenzte Bandbreite) | **Kante 2:** OpenClaw **pullt** die Queue über die OCSpline-API — Rollenlogisch korrekt für die kognitive Schicht. |
| Schnelle peripherische Antwort vs. langsame zentrale Verarbeitung | **Reflex-ACK &lt; 1 s** trennt schnelle Eingangsbestätigung von der langsamen Makrokette — analog zur Theorie-Latenz als Modellbestandteil (wenn auch hier eher UX/HTTP als explizites Gewicht). |
| Mehrere Eingänge, später gemeinsame Verarbeitung | **Kante 6** (Delivery-Receipt) und **Phase 6** (PE) führen Beobachtungen zurück in dieselbe Queue-/State-Welt — grob konsistent mit „Zusammenführung nach Persistenz“. |

---

## Was fehlt oder nur schwach abgebildet

1. **Priorität und normiertes Reiz-Envelope (§1: Zeitstempel + Priorität)**  
   Phase 1 nennt `correlation_id` und `queued`, nicht verbindlich **Priorität**, **normiertes Abweichungsmaß** am Eingang oder ein minimales **Ereignisschema** vor jeder weiteren Pipeline-Stufe. Risiko: „Interpretation“ (Routing, Filter) in Kong/Spline ohne dokumentierte Vereinheitlichung.

2. **Backpressure an der Afferenz-Grenze**  
   Theorie: System **entnimmt** mit Druckabbau; Annahme neuer Reize muss drosselbar sein. Im Entwurf: **Rate-Limits auf OpenClaw-Pulls** (§4), aber **keine explizite Admission Control** für Webhook-/Kong-Eingang (Kante 1) — klassische Lücke zwischen „Pull-Logik“ und real **push-getriebener** WhatsApp/Evolution-Zustellung.

3. **Stale-Policy / Latenzgewicht (§1: späte Signale mit abnehmendem Gewicht oder Verfallsdatum)**  
   `expected_arrival` + Timeout (Phase 2/6) ist eher **binär** (Frist / Tod) als **kontinuierliches Gewicht** oder explizite Stale-Klassen. Theorie ist reicher; Entwurf ist operativ, aber nicht isomorph.

4. **Vereinheitlichung vor Zusammenführung (Schema, Takt, Einheiten)**  
   Zwei Ströme (Nutzer-Nachricht vs. Delivery-Receipt) laufen über Kong → OCSpline. Abstrakt verlangt **einheitliches Schema vor Merge**. Der Entwurf liefert **Receipt-Integrität** (§4, Dedupe-Tupel) — gut — aber Phase 1 beschreibt nicht, dass **beide** Ströme dasselbe normierte Ereignis-/Metadaten-Format tragen, bevor sie dieselbe Zustandsmaschine berühren.

---

## Verletzungen / falsche Zuordnung (hart)

| Thema | Befund |
|-------|--------|
| **„Pull/Reiz-Eingang via Webhook“ (Kante 1)** | **Widerspruch zur üblichen und zur Mapping-Definition von Pull:** Ein Webhook ist **Push** vom Dienst zum Empfänger. Pull gilt sinnvoll für **OpenClaw → Queue**; die **Afferenz-Kante 1** ist transportseitig Push. Bezeichnung **„Pull“** für Kante 1 ist **theoretisch falsch** oder erfordert eine Präzisierung („Pull“ = nur mentales Modell „System holt sich Arbeit aus lokalem Buffer“, nicht Transportrichtung) — die steht im Dokument nicht da. |
| **Pflicht „nicht interpretieren vor Buffer“** | Solange Kong/Spline nur durchreichen und strukturieren, ist es ok. Jede semantische Vorverarbeitung **vor** `queued` wäre gegen §1; das ist im Draft **nicht ausgeschlossen** dokumentiert. |
| **Prediction Error als float-normiertes Maß (§1 + §5 A6)** | Phase 6 operationalisiert PE eher **boolean / diskret** (Veto, Timeout, failed) plus Trust-Collapse — **nicht** als durchgehend normiertes Abweichungsmaß an der Afferenz-/Workspace-Grenze. Diskrepanz zwischen Mapping-Layer und Makro-Kette. |

---

## Kurzfazit

- **Stärken:** Klare Trennung **Persistenz vor Kognition** (Postgres `queued`), **Pull der Kognition** von der Queue, Reflex vs. langsame Kette, Rückkopplung über Receipts und States.  
- **Schwächen:** **Webhook als „Pull“** bezeichnet — **Zuordnungsfehler**; fehlende explizite **Ingress-Admission** und **einheitliches Afferenz-Schema** laut §1; **Latenz/Stale** nur als Timeout, nicht als Gewicht; **PE** nicht als float-normiertes Konstrukt durchgängig.

**Empfehlung (1 Satz):** Kante 1 sprachlich in **Push (Transport) + lokaler Queue (Pull für Verarbeiter)** splitten; Phase 1 um **normiertes Reiz-Envelope, Priorität und Webhook-seitige Admission/Backpressure** ergänzen; optional Stale-Gewicht und kontinuierliches PE-Metrik-Feld mit A6 alignen.

---

*Evaluierung durch Sub-Agent (Orchestrator-Auftrag). Bezug: §1 Reiz & Afferenz vs. Master Draft §2 + Phase 1.*


[LEGACY_UNAUDITED]
