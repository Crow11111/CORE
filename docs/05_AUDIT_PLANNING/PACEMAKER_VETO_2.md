# PACEMAKER — Orchestrator B (Hugin) Review | Iteration 2

**Quelle:** `docs/05_AUDIT_PLANNING/SPEC_PACEMAKER.md` (Stand nach VETO-1-Überarbeitung)  
**Rolle:** Zero-Context Critic / asymmetrische Gegenkontrolle

---

## 1. NMI — hart und manipulationssicher?

**PASS (teilweise):** Die NMI-Matrix ist jetzt **disjunkt, zyklusbezogen und ohne Retry** definiert; Auslöser sind **äußere** Probes (HTTP 8000, Chroma-Heartbeat, Postgres, systemd `omega-event-bus`). Die Ausführung ist **physisch** (SIGKILL auf Prozessgruppe, kein weiches Event) — das erfüllt die Intention „hart“.

**VETO-Punkte (Restrisiko):**
- **OCBrain-Zielobjekt:** Weder PID-/PGID-Ermittlung noch Verifikation, dass wirklich der intendierte Prozess getötet wird — Manipulations-/Fehlziel-Risiko bleibt spezifikationsoffen.
- **`/tmp/omega_panic.lock`:** Als „fälschungssicher“ bezeichnet, aber ohne **Ownership, Modbits, Inhalt (z. B. PID/Timestamp/Nonce)** — unter Standard-Linux ist `/tmp` für andere Prozesse des Users typischerweise **nicht** kryptographisch oder mandantenfest „unfälschbar“.

---

## 2. Wertbeitrag (Metabolismus) — nicht fakelbar?

**PASS (teilweise):** „Wert“ ist an **persistente, kreuzprüfbare Spuren** gebunden (Chroma-Vektor mit frischerem Timestamp als letzter Takt **oder** neue Zeile `recall_memory`); reine Logs/Pings/PubSub sind **explizit verboten** — die offensichtliche „Log-Lücke“ aus Iteration 1 ist geschlossen.

**VETO-Punkt (Restrisiko):** Ein fauler Entwickler kann weiterhin **minimalen Junk** (leerer/sinnloser Eintrag, Embedding-Spam) in Chroma oder Postgres schreiben und damit den Decay **rein mechanisch** stillen — die Spezifikation fordert **keine** semantische oder quellenverifizierte Qualität des „Werts“. Zero-Trust: **Fake-Wert auf DB-Ebene bleibt möglich.**

---

## 3. Test-Doubles in den Traps explizit verboten?

**VETO:** Nur **Falle 1** verbietet Stubs/Mocks für die Chroma-Connection **ausdrücklich**. **Falle 2** und **Falle 3** enthalten **kein** analoges Verbot (z. B. gemockte DB, gemockter Timer/Recovery ohne echtes Dateisystem). Anforderung „in den Traps“ (Plural) ist damit **nicht vollständig** abgedeckt.

---

## Gesamturteil

| Kriterium            | Status        |
|---------------------|---------------|
| NMI hart verankert  | Stark, Lücken bei Ziel/Lock |
| Metabolismus anti-fake | Stark gegen Events-only, schwach gegen Junk-Commits |
| Test-Doubles in allen Traps verboten | **Nein** (nur Falle 1 explizit) |

**Ergebnis:** Es verbleiben spezifikationsrelevante Lücken → **VETO**.

**Empfohlene Nachschärfung (kurz):** (a) OCBrain- und Lock-File-Protokoll präzisieren; (b) „Wert“ um Mindestkriterien erweitern (z. B. Herkunftspfad, Größen-/Schema-Check, oder Operator-signierter Pfad — sofern im Scope); (c) in **allen** Veto-Traps **Test-Double-Verbot** oder „Integration-only“ explizit machen.

---

**Endstatus:** VETO


[LEGACY_UNAUDITED]
