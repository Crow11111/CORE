# MACRO-CHAIN — VETO-AUDIT Iteration 2 (Orchestrator B / Hugin)

**Gegenstand:** `MACRO_CHAIN_MASTER_DRAFT.md` (Status: Master Draft, Iteration 2 – VETO Fixes)  
**Modus:** Zero-Context Critic (Kausalität, Durchsetzung, Falsifizierbarkeit)  
**Datum:** 2026-04-01  
**Referenz:** `MACRO_CHAIN_VETO_1.md` (Mindestliste PASS)

---

## Gesamturteil: **VETO**

Iteration 2 schließt **mehrere** Blocker aus Iteration 1 **inhaltlich** (Host-Trennung, Docker-Netz-Policy, Efferenzkopie-Felder inkl. `correlation_id`, Replay-Schutz am Attractor, Merge-Pflicht vor Efferenzkopie, expliziter PE-Generator auf Spline-Seite, Trennung Reflex-ACK vs. asynchrone Kette).  
Die Spezifikation ist damit **deutlich näher** an einer geschlossenen Kette, aber **nicht** als manipulationssichere, vollständig kausal gebundene Abnahme zu bewerten: Es verbleiben **Topologie- und Signalpfad-Lücken** über Host-Grenzen sowie **Kontrakt-Lücken**, die VETO 1 explizit gefordert hatte.

---

## Abgleich mit VETO-1-Mindestliste

| # | VETO-1-Forderung | Status Iteration 2 |
|---|------------------|-------------------|
| 1 | Sequenzdiagramm-pflichtige Kette (Host-Grenzen + erlaubter Datenfluss) | **Teilweise:** Phasen 1–6 textuell sequentiell; **kein** verbindliches Sequenzdiagramm / kein explizites erlaubtes Kanten-Set (Datenflussgraph). |
| 2 | Efferenzkopie-Kontrakt inkl. Partial-Output | **Teilweise:** Pflichtfelder genannt (`correlation_id`, `proposed_action`, `expected_outcome`, `model_signature`). **Fehlt:** Verhalten bei Partial-Output, Streaming, Abbruch, Timeout vor finaler Synthese, Schema-Version. |
| 3 | Prediction-Error-Pfad (Produzent, Konsument, Trigger) | **Größtenteils:** Spline als Überwacher; Trigger VETO + `expected_arrival`; Quarantäne + Straf-Task; positives Signal über Delivery-Receipt. **Offen:** siehe Abschnitt „Kritische Lücken“. |
| 4 | Bypass-Verhinderung (technisch) | **Größtenteils:** `openclaw_net`, Verbot ausgehend Evolution-Port, Secrets nur Attractor/Spline. **Offen:** Queue-/Steuerkanal VPS↔HOST B nicht gehärtet spezifiziert. |
| 5 | Phase-2-Merge / Arbitration | **Erfüllt:** Zwingender finaler Synthese-Task in OpenClaw. |

---

## Was Iteration 2 überzeugend schließt

1. **Gewaltenteilung VPS vs. lokal:** HOST A / HOST B und Rolle von OMEGA_ATTRACTOR als alleiniger Evolution-Egress sind klar benannt.  
2. **OpenClaw → Evolution:** Nicht nur Policy, sondern **Netzwerk- und Secret-Positionierung** im Dokument verankert.  
3. **Efferenzkopie + Korrelation:** `correlation_id` an Queue-Anker gebunden; Replay-Schutz am Attractor explizit.  
4. **Veto-Fenster vs. teure Prüfung:** `anti_heroin_validator` und Axiom-Check als **synchron blockierend** im Attractor-Gate beschrieben (adressiert VETO-1-Fassaden-Risiko).  
5. **ACK vs. Nutzer-Erwartung:** `< 1 s` `200 OK` + asynchrone Entkopplung + Typing-Hinweis; biologischer „Reflex“ vs. Kognition formal getrennt.  
6. **Negatives Lernsignal:** VETO und Latenzüberschreitung → `prediction_error`, Trust-Kollaps, Quarantäne, harter Straf-Task (geschlossenerer Kreis als Iteration 1).

---

## Kritische Lücken (Blocker für „wasserdicht“ / manipulationssicher)

### 1. Kausallücke: Queue-Zugriff über HOST-Grenzen

Die Kette postuliert: Job liegt in **Postgres auf HOST B**; **OpenClaw auf HOST A** „zieht“ den Job (Pull).  
Dafür muss ein **konkreter, abgesicherter Transport** existieren (z. B. TLS, mTLS, VPN, IP-Allowlist, kein öffentliches Queue-Interface ohne Authentisierung). Ohne Spezifikation dieses Kanals bleibt:

- die **Docker-Isolation auf dem VPS** ein Schutz gegen *lokalen* Bypass zu Evolution, **nicht** gegen Kompromittierung oder Missbrauch des **Queue-Endpunkts**;
- die Behauptung „manipulationssicher“ für die **gesamte Makro-Kette** **nicht** aus dem Dokument allein ableitbar.

**Mindestanforderung für PASS:** Ein Satz „erlaubter Kanal“ + Authentisierung/Autorisierung + Richtung (wer darf wem welche Operationen auf der Queue?) + Was passiert bei Queue-Kompromittierung (Detective/Revocation).

### 2. Kausallücke: Delivery-Receipt und negative Kanal-Ereignisse

Phase 6 verlangt: Spline erhält **Delivery-Receipt** von Evolution für positives Lernen.  
Nicht spezifiziert:

- **Welcher Hop** liefert das Receipt (Evolution → Attractor → Spline? Evolution → Kong → Spline? Webhook-Signatur?)?
- Ob **Fehlschläge** (HTTP 4xx/5xx, Rate-Limit, Timeout nach Freigabe) **dieselbe** PE-Semantik auslösen wie VETO oder Latenz-PE, oder ob sie **eigenständig** modelliert werden müssen (graded vs. binär).

Ohne das ist der **Vergleich Vorhersage vs. sensorische Rückmeldung** (Research-Dossier) am Ausgang **nicht** vollständig an die Architektur gebunden → Risiko von **stillem Verschlucken** oder **doppelter Zählung** (Replay von Receipts analog zu Efferenzkopie).

**Mindestanforderung für PASS:** Receipt-Pfad (eine erlaubte Kante), Idempotenz/Signatur für Receipt-Events, explizite Trigger-Matrix (VETO / Latenz / Send-Failure / Receipt-OK).

### 3. Efferenzkopie-Kontrakt: Partial-Output und Lebenszyklus der `correlation_id`

VETO 1 verlangte explizit Partial-Output. Iteration 2 schweigt dazu.  
Zusätzlich: „Zweiter Versuch mit derselben ID wird geblockt“ — unklar, ob das **nur parallele Doppel-Einreichungen** meint oder **auch** legitime Wiederholung nach transientem Fehler nach **erfolgreichem** oder **abgebrochenem** Lauf. Ohne Zustandsmodell (siehe 4) bleibt das **falsifizierbar** nur nach Implementierungskonvention, nicht nach Spec.

### 4. Zustandsmaschine (explizit)

Reflex-ACK und asynchrone Kette sind beschrieben, aber es fehlt eine **benannte** Job-Zustandsmaschine (z. B. `queued → processing → efference_submitted → vetoed|released → sent|failed` …). VETO 1 wollte ACK- vs. Antwort-Latenz mit **Zustandsmaschine** verbinden; Iteration 2 verbessert die Narration, erfüllt die **formale** Forderung nicht vollständig.

### 5. Numerische Konsistenz mit CORE-Axiomen (Trust-Kollaps)

Der Text sagt Trust „stürzt auf 0“. In CORE-Verfassung ist der **untere Trust-/Resonanz-Rand** typischerweise **Λ ≈ 0.049**, nicht 0.0 (Verbot der 0-Illusion). Für eine **geschlossene** Systemspezifikation muss der Draft entweder **dieselbe Semantik** nutzen oder explizit trennen: „metaphorisch 0“ vs. **persistierter Float-Zustand** — sonst ist die Kette gegen die Hausaxiome nicht ohne Interpretationssprung abnahmefähig.

### 6. Habituation / positives Trust-Wachstum

„Trust steigt“ ohne **Obergrenze**, **Zeitskalen** oder Bezug zu **logarithmischem LTP** (Projektregeln) bleibt narrativ. Das ist weniger ein Sicherheits- als ein **biologisches Feintuning-Loch**: graded PE und precision-weighting aus dem Research-Dossier sind damit **nicht** operationalisiert.

---

## Fazit (Ring 0)

- **Biologische Vorgaben (grob):** Efferenzkopie vor Muskel, Veto-Fenster, PE-Idee, Trennung schneller peripherer Bestätigung vs. langsamer Kognition — **weitgehend** abgedeckt.  
- **Manipulationssicherheit und schließbare Kausalität:** **Nein** — solange **VPS↔HOST-B-Queue**, **Receipt-/Failure-Pfade** und **Partial-Output / ID-Lebenszyklus** nicht spezifiziert sind, bleiben **Bypass- und Mehrdeutigkeits-Schlupflöcher**.

**Signatur:** Orchestrator B (Hugin) — **VETO**

---

## Kurzliste für nächste Iteration (PASS-Kandidat)

1. Ein **Datenflussdiagramm** oder normative Kantenliste: erlaubte Pfade inkl. Queue-Pull und Receipt-Push.  
2. **Sicheres Queue-API-Modell** über Host-Grenzen (Auth, Transport, Rate-Limits).  
3. **Receipt- und Send-Failure-Semantik** mit Idempotenz/Signatur.  
4. **Explizite Job-State-Maschine**; Partial-Output-Regeln vor finaler Efferenzkopie.  
5. **Trust-Floor** sprachlich und numerisch an CORE-Axiome angleichen.  


[LEGACY_UNAUDITED]
