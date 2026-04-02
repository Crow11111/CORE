# MACRO-CHAIN vs. Biologie→Digital (Ebene 2): Harte Abgleichsnote — Agent 3

**Bezug:** `docs/01_CORE_DNA/BIOLOGY_TO_DIGITAL_MAPPING.md` (§3 Efferenzkopie / Commit-Grenze, §4 Liveness & Admission Control) gegen `docs/05_AUDIT_PLANNING/MACRO_CHAIN_MASTER_DRAFT.md` (Phase 3–6).

---

## Was passt (Alignment)

| Theorie (L2) | Entwurf (L3) |
|--------------|----------------|
| **Intent vs. Ausführung** als getrennte Schichten | Klar: OpenClaw synthetisiert (Phase 2–3), Ausführung nur über Attractor → Evolution (Phase 4–5). |
| **Efferenzkopie** als „Vorab-Bild“ vor dem Muskel | Phase 3: strukturierte Payload mit `correlation_id`, `proposed_action`, `expected_outcome` an OMEGA_ATTRACTOR vor physischer Sendung. |
| **Free Won’t / Veto vor Commit** | Phase 4: synchrones Veto-Fenster auf dem VPS vor Evolution-Call; `vetoed` vs. `released`. |
| **Prediction Error als operatives Signal** (nicht Meinung) | Phase 6: Veto, Timeout (`expected_arrival`), fehlgeschlagenes Delivery-Receipt → definierter „Schmerz“-Pfad; Erfolgspfad über Receipt. |
| **Evidenz vor Vertrauen (A7-Ansatz)** | Idempotenz/Replay-Schutz (`correlation_id`, 409), Signatur-Pflicht für Receipts (§4 Master-Draft) unterstützen Abgleich statt blindem Weiterreichen. |

---

## Was fehlt oder nur implizit ist (Lücken)

1. **Forward Model = Dry-Run vor irreversiblen Seiteneffekten**  
   L2 verlangt explizit **Simulation/Dry-Run** (Zustandsdelta, Kosten, Risiko) *vor* irreversiblen Wirkungen. Phase 3 nennt `expected_outcome`, operationalisiert aber keinen **verpflichtenden** Dry-Run-Schritt oder nachprüfbares Artefakt (z. B. separates Simulationsergebnis, das der Attractor unabhängig validieren kann). Risiko: „Efferenzkopie“ wird zur reinen Deklaration ohne nachweisbare Vorab-Simulation.

2. **Efferenzkopie-Abgleich (eigenes Kommando vs. fremder Reiz)**  
   L2: externe Beobachtung mit **intern vorhergesagter** Rückkopplung abgleichen. Phase 6 nutzt Receipts und Timeouts, beschreibt aber nicht den **semantischen** Abgleich `expected_outcome` ↔ beobachtete Liefer-/Inhalts-Evidenz. PE als *Differenzmaß* (normiert, float) fehlt im Makro-Fluss; es dominieren binäre Trigger.

3. **Point of No Return / Commit-Grenze benannt und verortet**  
   L2: nach Überschreiten nur noch **kompensierende** Aktionen. Im Draft ist die **exakte** Commit-Linie unklar: `released` + Attractor ruft Evolution? Erst nach erfolgreichem Send? Was passiert bei Teilfehlern nach `released` (kein Rollback durch „Vergessen“ — ist spezifiziert, *wie* kompensierend reagiert wird)? Rechte/Pflichten der Ebenen nach PoNR sind nicht explizit.

4. **Liveness-Vertrag (Heartbeat)**  
   L2: periodisches Signal, harte Toleranz, Ausbleiben = **terminal**, kein Retry-Pingpong; Verlust der Liveness auf tieferen Ebenen → **Commit-Stopp** höher. Phasen 3–6 enthalten keinen **kanonischen** Heartbeat zwischen OCBrain, Attractor und Spline/Queue; `expected_arrival`/Pacemaker (Phase 2/6) ist Timeout/Schmerz, aber nicht derselbe Vertrag wie „Heartbeat = Liveness-Garant für Fortführung der Kette“.

5. **Ressourcenbilanz, Entropie-Drift, Admission Control (§4)**  
   L2: festes Zeitfenster, SNR/Informationsgewinn vs. Verbrauch, Drift gegen 0.951 → **Circuit Breaker**, Block neuer Ereignisse, **logarithmische** Worker-Reduktion, Degradationsstufen. Der Draft hat Rate-Limits/JWT-Revocation (§4 Härtung), aber **keine** Abbildung der Drift-Metrik, der 0.951-Schwelle und der deterministischen Drosselung **innerhalb** der Makro-Phasen 3–6 als Pflicht.

---

## Wo Rechte/Pflichten verletzt oder verschoben wirken

| Thema | Bewertung |
|-------|-----------|
| **Veto-Fenster** | L2: Veto **vor** Commit. Zuordnung Attractor→Evolution ist stimmig. **Lücke:** kein zweites, zeitlich versetztes aber noch wirksames Bremselement (z. B. Queue-Seite), falls Attractor kompromittiert oder logisch übersprungen wird — Härtung §4 reduziert Netzwerk-Bypass, ersetzt aber nicht die theoretische „spätere, noch wirksame“ Bremsinstanz als **explizite** Rolle. |
| **Irreversibilität** | Ausführung liegt bei Evolution (Phase 5) — plausibel irreversibel. **Risiko:** ohne benannte PoNR und ohne Pflicht-Abgleich Prediction↔Observation bleibt die Commit-Grenze für Audits und für „kompensierend statt rollback“ schwammig. |
| **Heartbeat / Liveness** | Pflicht aus §4 ist im Makro-Ablauf 3–6 **nicht** als harter Querschnitts-Vertrag abgebildet; nur Teilmenge (Timeout/Schmerz). Das kann **Commit-Stopp bei unterer-Ebenen-Ausfall** unterdefinieren. |
| **Admission Control** | Rate-Limits ≠ **Admission Control** im Sinne von Drift-Schwelle und systemweitem Annahmestopp. Zuständigkeit (wer blockiert neue Jobs — Spline, Attractor, beide?) und Kopplung an L2-Metriken fehlen in Phase 3–6. |

---

## Kurzfassung

Der Entwurf trifft **Intent/Ausführung**, **Efferenz vor Muskel**, **Veto vor Evolution** und **grobe PE-Rückkopplung** gut. Er untererfüllt L2 dort, wo **Forward Model** als nachweisbarer Dry-Run, **Efferenzkopie** als strikter Vorhersage↔Beobachtung-Abgleich, **explizite Commit-Grenze mit kompensierendem Nachlauf**, **Heartbeat-Liveness mit Commit-Stopp** und **vollständige Admission-Control-/Drift-Logik** gefordert sind. Empfehlung für nächste Iteration: PoNR-Zustand im Zustandsdiagramm; verpflichtendes `expected_outcome`-Matching im Receipt-Pfad; Heartbeat-Matrix (Wer? Periode? Terminalverhalten?); Drift/Circuit-Breaker als erste Klasse neben Rate-Limit.

---

*Agent 3 — Evaluierung nur Theorie↔Draft; keine Implementierungsbehauptungen.*


[LEGACY_UNAUDITED]
