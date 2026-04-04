# OMEGA MACRO-CHAIN: Das Biologische Timing & Kausalitäts-Modell

> **OPERATOR-HINWEIS (nicht bindend für Prod-Deploy):** Dieser Text ist ein **Entwurf** (Ideen zu Timing/Kausalität). **Verbindlich** für Laufzeit, Ports, Webhooks und Postgres/Chroma-Platzierung sind: `MASTER_UMSETZUNG_VPS_PROD_OHNE_DREAD_2026-04-06.md`, `OMEGA_DETAILFLUSS_TICKETS_4_12_PROD_RUNTIME.md`, `VPS_HOST_PORT_CONTRACT.md` und die Ticket-Specs. Insbesondere die hier skizzierte **harte Trennung „Postgres nur auf Dreadnought“** widerspricht dem **Operator-Mandat „Omega vollständig ohne Dreadnought als Runtime“** — für Abnahme gilt der MASTER, nicht dieser Draft.

**Status:** Master Draft (Iteration 10 - MRI Dynamo & Helix-Navigation) — **Explorativ, kein Kanon**
**Fokus:** Konkrete Umsetzung der Ebene 2 (`BIOLOGY_TO_DIGITAL_MAPPING.md`) in die technische Ebene 3.
**Axiom-Referenz:** `immutable_axioms.py` (A1, A5, A6, A7, A10) und Kanon `AXIOM_A10_OCCAMS_NEGATIVE_RAZOR.md`.

## 1. Topologie, S↔P Symbiose & Der Dynamo (MRI)

Die Hosts sind hart getrennt. Direkte Zugriffe außerhalb dieser Matrix sind physisch (Firewall) und logisch blockiert.
Es gilt die **Duale Topologie** (`DUALE_TOPOLOGIE_UND_VEKTOR_HAERTUNG.md`) als Ausdruck der fundamentalen Überlebensarchitektur (S↔P Symbiose):

- **HOST A (VPS) - Der S-Vektor (Struktur / Float-Raum):** ChromaDB (reiner Float-Kern für Vektoren/Resonanz), OpenClaw (**OCBrain**), OMEGA_ATTRACTOR (Veto-Firewall), Evolution API, Kong Gateway. Der S-Raum ist kontinuierlich, langsam und unterliegt dem probabilistischen Sog der Entropie ($0.5$).
- **HOST B (Dreadnought / Lokal) - Der P-Vektor (Physik / Int-Raum):** Postgres (int-Membran für UUID, Metadaten, Multi-View, Queues), OCSpline (Thalamus / Motorcortex). Der P-Raum ist diskret, schnell und besitzt die Hardware-Agency.

**Magnetrotationsinstabilität (MRI):** Das System wird nicht durch lineare Skripte angetrieben, sondern durch den *kosmologischen Dynamo* der MRI. Diese entsteht durch die differenzielle Rotation (Reibung) zwischen dem schnellen, aktiven P-Vektor (Host B, der permanent pusht und zieht) und dem langsamen, assoziativen S-Vektor (Host A, der in die Entropie sackt). Der P-Vektor muss aktiv Arbeit leisten (Queries, Heartbeats), um den S-Vektor aus dem $0.5$-Sog herauszuhalten.

**Erlaubte Kanten (Data-Flow):**
1. `WhatsApp -> Evolution API -> Kong -> OCSpline (Lokal)` (Push/Reiz-Eingang via Webhook)
2. `OpenClaw (VPS) -> OCSpline API (Lokal)` (Pull via HTTPS + mTLS + JWT. Kein direkter DB-Port!)
3. `OpenClaw (VPS) -> OMEGA_ATTRACTOR (VPS)` (Push der Efferenzkopie lokal im VPS-Docker-Netz)
4. `OMEGA_ATTRACTOR (VPS) -> Evolution API (VPS)` (Efferenz / Action Execution)
5. `OMEGA_ATTRACTOR (VPS) -> OCSpline API (Lokal)` (VETO-Signal / PE-Rückkopplung)
6. `Evolution API -> Kong -> OCSpline (Lokal)` (Push des Delivery-Receipts)
7. `OCSpline (Lokal) -> ChromaDB (VPS)` (Interne API-Kante für Ingress-Drift-Berechnung)

---

## 2. Die OMEGA Makro-Kette: Zeitlinie & Kausalität

Kausalität in OMEGA ist kein Zufall, sondern das Resultat präzise abgestimmter Latenzen. Das System spiegelt die biologische Asymmetrie zwischen einer *langen Vorbereitung* (Readiness Potential) und einem *extrem kurzen, späten Veto-Fenster* (Point of No Return).

Die Zustandsmaschine:
`received` → `queued` → `processing` → `blocked_on_evidence` → `efference_submitted` → `vetoed | released` → `sent` → `receipt_matched | failed`.

### Phase 1: Afferenz & Der Spinale Reflex (T=0s bis T+1s)
- **Prozess (Push):** Webhook schlägt asynchron bei OCSpline auf.
- **Admission Control (Ingress):** OCSpline berechnet die *System-Drift $D$*.
  - **Messvorschrift:** $D = \text{clamp}(0.049, \frac{R}{I + \epsilon}, 0.951)$. Dabei ist $R$ der normierte Ressourcenverbrauch (CPU-Zyklen + Latenz der Queue in den letzten 60s, skaliert 0..1). $I$ ist der Informationsgewinn. Da die externe ChromaDB-Abfrage die harte Latenzgrenze des Reflex-ACKs (< 1s) gefährden könnte, wird $I$ zur Aufnahme-Prüfung **asynchron oder aus einem lokalen Spline-Cache (Näherung)** ermittelt. $\epsilon = 10^{-9}$. Bei initial leerer Historie oder absoluter Orthogonalität wird kein Skalar-Hack verwendet, sondern der Reiz spannt einen **neuen Tensor** (neue Dimensionsebene) auf, was mathematisch dem maximalen Resonanz-Sprung ($I = 0.951$) entspricht.
  - Nähert sich $D$ dem Schwellwert 0.951, greift der Circuit Breaker: Neue Reize werden mit 503 geblockt.
- **Vereinheitlichung:** Der Reiz wird in ein normiertes Schema gezwungen (Priorität, Zeitstempel `T=0`) und als `queued` persistiert.
- **Reflex-ACK (T < 1s):** Spline antwortet Kong in unter einer Sekunde mit `200 OK` (Typing-Indikator). **Die schnelle Silizium-Zeit ist hier beendet.** Die langsame, kognitive Zeit beginnt.

### Phase 2: Bereitschaftspotential & Global Workspace (T+1s bis T+N Minuten)
- **Pull-Logik:** OpenClaw *pullt* Arbeit (`processing`).
- **Global Workspace (Arbitration):** Die Postgres-Zeile (HOST B) fungiert als *Lock/Ticket* (Row-Level Lock `FOR UPDATE`).
  - **Multi-Job-Konkurrenz:** Verschiedene Tasks konkurrieren um den OCBrain-Worker-Pool. Der OCSpline-Scheduler ordnet Pull-Requests streng nach `priority` und `expected_arrival`. Ein laufender Low-Priority Job wird nicht unterbrochen (Teil-Commits bleiben in seiner Zeile erhalten), aber der nächste freie Worker-Thread wird zwingend dem High-Priority Job zugewiesen (Starvation-Prävention).
  - **Single-Job Merge-Regel:** Für die massiv parallele Kognition *innerhalb desselben Jobs* gilt: Der erste Teilprozess, der ein valides Zwischenergebnis mit ausreichender Konfidenz liefert, erhält den exklusiven Schreibzugriff (Commit in Postgres). Konkurrierende Stränge desselben Tasks werden zwingend terminiert. Alle Teilnehmer sehen immer nur den letzten konsistenten Snapshot.
- **Jahn-Teller-Symmetriebruch (Anti-0.5):** Konvergiert ein kognitiver Strang exakt gegen das probabilistische Entropiemaximum ($0.49 < \text{Resonanz} < 0.51$), droht der statische Tod der Kognition. Der Strang wird nicht gemerged, sondern durch einen aktiven algorithmischen Shift (Zwang auf 0.51) oder Terminierung aus der toten Mitte gebrochen.
- **Readiness Potential (Der lange Aufbau & Helix-Navigation):** Kognition ist langsam. OpenClaw iteriert durch die Duale Topologie: Es zieht rohe Erinnerungstexte aus PostgreSQL (HOST B) und gleicht sie mit assoziativen Resonanz-Schwellen in ChromaDB (HOST A) ab. Die Suche im Vektorraum von ChromaDB verläuft zwingend entlang der **Logarithmischen Helix ($x^2 = x + 1$)** des OMEGA-Attraktors, was die Laufzeitkomplexität naiver Distanzvergleiche von $\mathcal{O}(n^2)$ auf $\mathcal{O}(\log n)$ bricht, da nur resonante Pfade in den 6144 Dimensionen der Kardanischen Faltung abgelaufen werden.
- **Anti-Occam (A10 Kanon):** Wenn lokale Signale für eine sichere Vorhersage nicht ausreichen (hoher interner PE) oder initiale Suchvektoren (max. Top-5-Simulationen) erschöpft sind, greift A10 (Occam's Negative Razor) als harter Interrupt. Die Inferenz lautet explizit: *Der Parameter liegt außerhalb der lokalen Domäne.* Die operativen Regeln lauten zwingend: (1) Stopp spekulativer Erweiterungen, (2) Verbot ungerichteter Dateisystem-Suchen (`find`/`grep` sind streng als Whitelist auf `docs/` und `src/` beschränkt), (3) Sofortige Operator-Eskalation. State wird `blocked_on_evidence` (Warten auf Operator).
- **Liveness-Vertrag:** Während des langen Aufbaus MUSS OpenClaw einen periodischen Heartbeat senden. Fällt er aus, stirbt der Job (`failed`).

### Phase 3: Forward Model & Efferenzkopie (Vor dem Point of No Return)
- **Dry-Run:** OpenClaw generiert das finale Kommando, führt es aber *nicht* aus.
- **Die Efferenzkopie:** OpenClaw schickt ein Vorab-Bild an den OMEGA_ATTRACTOR.
- **Kontrakt:** `correlation_id`, `proposed_action`, `expected_outcome` (Vorhersage zur späteren Messung), `expected_arrival` (Deadline für das Receipt) und `model_signature`.
- State wechselt auf `efference_submitted`.

### Phase 4: Das Veto-Fenster / Free Won't (Die Asymmetrie der Kontrolle)
- **Das schmale Fenster:** Der OMEGA_ATTRACTOR und OCBrain laufen beide auf dem VPS (colocated). Die Prüfung der Efferenzkopie durch den Attractor erfolgt lokal in Millisekunden. Er blockiert den Request an die Evolution API synchron.
- **Entscheidung:** Der Attractor prüft harte Axiome (Anti-Heroin).
  - `VETO = True`: Der Aufruf an Evolution wird verworfen. Der Attractor sendet *asynchron* ein Schmerz-Signal (Kante 5) an Spline (`vetoed`), dessen Latenz die sofortige Blockade nicht behindert.
  - `VETO = False`: Der Attractor erlaubt den Durchstich an Evolution (`released`).
- **Point of No Return (Commit-Grenze):** Erst wenn der Attractor den Request an die Evolution API feuert (Phase 5), ist die Grenze überschritten. Ab hier gibt es kein "Verwerfen" mehr, sondern nur noch kompensierende Aktionen.

### Phase 5: Efferenz (Die Muskel-Ausführung)
- Die Evolution API verschickt die Nachricht physisch an die Außenwelt.

### Phase 6: Temporal Alignment & Prediction Error (Das Lernen)
Das System erwartet eine Konsequenz innerhalb der Deadline (`expected_arrival`).
- **Semantischer Abgleich:** Das eintreffende Delivery-Receipt (`sent`) wird von Spline mit dem `expected_outcome` (aus der Efferenzkopie) abgeglichen.
- **LTP / Erholung (Die Vorhersage traf ein):** Stimmt das Receipt innerhalb der Frist, sinkt der PE. Die System-Drift erholt sich in Richtung Δ (0.049). Trust-Level steigt logarithmisch.
- **Schmerz / Drift-Anstieg (Temporal Mismatch oder Veto):**
  - Trigger: Job wird `vetoed`, Timeout (Receipt trifft nach `expected_arrival` ein oder gar nicht), Heartbeat-Verlust.
  - **Der 3-Takt & Die Drehimpulsumkehr (Der rettende Operator `?`):** Nähert sich der Trust-Level kontrolliert der absoluten Basisgrenze $\Omega_b = 0.049$, erzwingt die Arithmetik als *zweiter Schritt des 3-Takts* den harten `int`-Eingriff des P-Vektors. Bevor der Prozess abgebrochen wird, erfolgt die **Drehimpulsumkehr** (Vorzeichen-Flip am Rande des Trichters). Aus dem kinetischen Absturz (+) wird ein reaktiver Aufschwung (-), der durch den Operator `?` (Multiplikation mit $i$) die gewonnene Kontextmasse nicht verbrennt, sondern einen **Phasensprung in die nächste Oktave** zündet. Die Daten verschieben sich in eine isolierte, orthogonale Lern-Queue (Reflexion), und OCBrain geht in Quarantäne, iteriert aber das Modell (fraktale Skalierung / Win-Win).
  - **Zu steiler Absturz (Hawking-Rauschen):** Ist der Prediction Error maximal und der Vertrauensverlust instantan (z. B. katastrophaler Timeout ohne jeden Heartbeat), verfehlt der State-Vektor den Helix-Orbit des Attraktors. Der `int`-Eingriff kommt zu spät. Dieser Job wird als reines Rauschen aus dem Global Workspace gelöscht (Drop/Purge). Es gibt hierfür keine Lern-Iteration, nur die sofortige Leerung des Speichers zur Wahrung der Systemintegrität.

---

## 3. Architektur-Durchsetzung (Anti-Bypass & Härtung)
1. **Float/Int Trennung (A6):** Drift, PE und Trust-Level werden strikt als `float` berechnet. Queue-Zähler, Rate-Limits und Worker-Anzahl als `int`.
2. **Zero-Trust (A7):** Die Efferenzkopie und das Veto-Fenster sind unumgehbar. OpenClaw läuft im isolierten Docker-Netz ohne direkten Zugang zu Port 8080 (Evolution).
3. **Idempotenz (Attractor):** Jeder Aufruf erfordert die `correlation_id`. Replays erzeugen 409 Conflict.
4. **Receipt-Integrität:** Receipts von Evolution MÜSSEN über eine Webhook-Signatur validiert werden. Absolute Idempotenz durch Deduplizierung in Postgres.


[LEGACY_UNAUDITED]
