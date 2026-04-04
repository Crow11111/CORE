# TICKET-12: Drei Architektur-Konzepte — Sentinel-Daemon & Traumschleife (Topological Void Detection)

**Modus:** System-Architekt (Ring 0)  
**Status:** Architektur-Alternativen (nicht O2-geprüft)  
**Bezug:** [`TICKET_12_EPISTEMIC_DRIVE.md`](./TICKET_12_EPISTEMIC_DRIVE.md) — epistemischer Antrieb auf dem VPS neben OpenClaw (HA-Bus, Vision, Idle-Scans).

---

## 0. Ziel und Bewertungsdimensionen

Dieses Dokument entwirft **drei grundverschiedene** physische Arrangements für:

1. **Sentinel-Daemon** — dauerhafte oder nahezu latenzarme Aufnahme normalisierter Eingaben (HA-WebSocket, Vision-Anker, MQTT/Webhooks) in eine **Ingest-Queue** ohne finale Weltwirkung.
2. **Traumschleife** — **Topological Void Detection** in Idle-Phasen über ChromaDB plus nachgelagerte, policy-gefesselte Synthese (OpenClaw-APIs).

Jedes Konzept wird bewertet gegen:

| Dimension | Bedeutung |
|-----------|-----------|
| **A7 (Zero-Trust / Evidenz)** | Jeder interne und externe Schritt ist verifizierbar: AuthN/Z, Audit-Spur, kein stilles Verwerfen von Events ohne protokollierte Policy (vgl. Ticket 12 §1.3–1.4). |
| **A6 (Float / Resonanz)** | Zustände wie Priorität, Konfidenz, Schwellen leben in der **Resonanzdomäne** (Float), keine diskreten „0/1/0.5“-Kunstgriffe für Steuerungslogik (A5/A6). |
| **Latenz** | Zeit von Rohereignis bis sichtbarer Ingest-Record bzw. bis Void-Erkennung startet; auch Rückkopplung zu Operator-Last. |
| **OMEGA-Architektur** | Passung zu Tetralogie, Membran (Ticket 11), Apoptose vs. Idle-Lernen, klare Trennung **Inbound (Ticket 12)** vs. **Outbound-Veto (Ticket 10/11)**. |

---

## Konzept 1 — Integraler Monolith-Daemon („Ein Prozess, eine Wahrheit“)

### Architektur

Ein **einzelner langlaufender Prozess** (z. B. Python `asyncio`), der im selben Adressraum (oder einem eng gekoppelten Sidecar im selben Compose-Stack):

- **HA** über dauerhafte WebSocket- oder Long-Poll-Verbindung hält, Events normalisiert und in eine lokale Queue schreibt (Redis Streams, SQLite WAL-Queue oder In-Memory mit spill-to-disk).
- **Vision** nur als **diskrete Anker-Events** einliest (eigener Thread/Subprozess oder IPC), keine Voll-Pixel-Pipeline im Hot-Path des Hauptloops.
- **Cron-äquivalent** (APScheduler, interne Timers) für **Void-Scans** und periodische **Chroma-Stichproben** in Idle-Fenstern ausführt.
- **OpenClaw** direkt per HTTP/gRPC aufruft (Forschungsfragen, Einbettung, Policy-gates), sobald Void-Tickets die Resonanz-Schwelle überschreiten.

Supervision: **systemd** oder **Docker Compose** mit Restart-Policy; ein **Health-HTTP-Port** oder Heartbeat-File.

### Sentinel in diesem Modell

Alles läuft **sequenziell koordiniert** im gleichen Scheduler: Backpressure = eine zentrale Policy-Funktion (Drop mit Audit, Downsampling).

### Traumschleife in diesem Modell

Void-Heuristiken (k-NN-Lücken, Coverage-Gaps) als **Bibliotheksaufrufe** im selben Prozess; Ergebnis → Void-Tickets im gleichen Speicher/DB-Handle.

### Vor- und Nachteile

| Kriterium | Einschätzung |
|-----------|--------------|
| **A7** | **Pro:** Ein zentraler Ort für Logging, Trace-IDs, Policy-Checks vor jedem OpenClaw-Call. **Contra:** Fehler oder Kompromittierung des Monolithen betrifft **alle** Kanäle; Secrets konzentriert — Zero-Trust erfordert strikte **interne** Aufteilung (Module mit eigenen Tokens) und harte Read-Only-DB-Rollen trotz eines Prozesses. |
| **A6** | **Pro:** Resonanz-Floats (Priorität, Konfidenz) können durchgängig als `float` in einer gemeinsamen Domäne gereicht werden, ohne Serialisierungs-Brüche Int↔Float. **Contra:** Versuchung, für „einfache“ Flags Integer-Enums zu nutzen — muss im Implementierungs-Ticket explizit verboten werden. |
| **Latenz** | **Pro:** Ingest oft **niedrig** (kein Netz-Hop zwischen Microservices). **Contra:** CPU-lastige Void-Scans können den Event-Loop **blockieren**, wenn nicht in Worker-Threads/ProcessPool ausgelagert — sonst steigt E2E-Latenz für HA unter Last. |
| **OMEGA** | **Pro:** Klare Story für den Operator: „Ein Sentinel-Dienst.“ Passt zur Ticket-12-Formulierung „dedizierter Daemon“. **Contra:** Skalierung und unabhängiges Deploy von „nur Ingest“ vs. „nur Traum“ sind schwer; Abstimmung mit Ticket-11-**Apoptose** muss explizit im Scheduler modelliert werden (gemeinsame Idle-Erkennung). |

---

## Konzept 2 — Event-getrieben, entkoppelt („HA pusht, Void konsumiert“)

### Architektur

**Kein** fetter Dauer-WebSocket zwingend im Kern: Stattdessen **Push nach innen**:

- **Home Assistant** (oder ein schlanker HA-Connector auf dem VPS) sendet **Webhooks** oder **MQTT** an einen **Edge-Ingress** (z. B. Kong, Traefik, oder Caddy mit mTLS) → validiert → schreibt in eine **Queue** (Redis Streams, NATS, RabbitMQ).
- **Kleine Worker** (Container oder `systemd`-Oneshots), die aus der Queue lesen: Normalisierung, Dedupe (Idempotenz-Keys), optional Anreicherung, dann Persistenz/Event-Store-Pfad.
- **Void-Detection** als **separater Consumer** oder geplanter **Job-Runner** (z. B. Nomad/K8s CronJob, oder einfach `systemd timer`), der nur startet, wenn die Queue **tief** ist und OpenClaw als „idle“ gemeldet hat — oder wenn ein **„void_scan_requested“**-Message-Typ explizit eingereiht wird.

OpenClaw wird **nicht** vom HA-Hot-Path aufgerufen, sondern nur von einer **Synthese-Worker**-Einheit mit Allowlist und Rate-Limits.

### Sentinel in diesem Modell

Der „Sentinel“ ist **verteilt**: Ingress + Queue + ein oder mehrere **Stateless Consumer**. Dauer-Verbindung zu HA kann in einem **minimalen Bridge-Container** stecken, der nur übersetzt und published.

### Traumschleife in diesem Modell

Topological Void Detection ist **batch- oder stream-sekundär**: z. B. nächtlicher Scan + zusätzliche Trigger bei „Queue leer + kein Chat“ über ein Signal von OpenClaw.

### Vor- und Nachteile

| Kriterium | Einschätzung |
|-----------|--------------|
| **A7** | **Pro:** Klare **Perimeter** — jeder Webhook/JWT/mTLS-Schritt ist separat auditierbar; Blast-Radius bei Kompromittierung eines Workers begrenzt. **Contra:** **Mehr bewegliche Teile** — jede Übergangskante braucht Auth und Log-Korrelation (Trace über Queue-Metadaten), sonst entstehen „stille Lücken“ entgegen Ticket 12. |
| **A6** | **Pro:** Message-Payloads können `priority_float` und Konfidenz als Float tragen (JSON-Schema). **Contra:** Viele Queues und DBs serialisieren numerisch — **Rundung und NaN** müssen verboten/normalisiert werden; keine implizite Integer-Priorität in Broker-Priority-Levels ohne Mapping-Policy. |
| **Latenz** | **Pro:** HA-Hot-Path kann **extrem kurz** sein (Fire-and-forget mit ACK). **Contra:** Kaltstart von Serverless/Oneshot-Jobs und zusätzliche Netz-Hops erhöhen **Tail-Latenz**; Void-Erkennung ist ohnehin **nicht** Echtzeit-kritisch, aber **Coverage-Gap-Heuristiken** brauchen konsistente Zeitachsen über alle Worker. |
| **OMEGA** | **Pro:** Entspricht gut der **Membran-Idee**: Ingest ist „Rohmembran“, Synthese ist separater Strang mit Outbound-Policy. **Contra:** Scheduling **Idle ↔ Apoptose** (Ticket 12 §4) erfordert einen **Orchestrierungs-Bus** oder gemeinsamen Zustand; ohne den entsteht Wettlauf zwischen „Traum füllt Chroma“ und „Apoptose löscht Rauschen“. |

---

## Konzept 3 — Neuromorph / Schlaf-Wach-Zyklus („Pacemaker steuert Wahrnehmen vs. Träumen“)

### Architektur

Ein **kleiner „Hypothalamus“-Daemon** (Steuerprozess) liest **kontinuierlich** einen **Pacemaker-Zustand** aus der OMEGA-Welt: z. B. Resonanz-/State-Vektor aus `core_state` oder einem dedizierten **Float-Store** (kleine DB oder Shared-Memory), der **V** (Vigilanz / Wachheit) und **R** (Ruhe / Rekombination) als **A6-konforme Floats** führt — nicht als boolesche „awake/sleep“.

- **Wach-Phase (hohe V, niedriger Traum-Anteil):** Ressourcen-Budget fließt in den **Sentinel**: HA-Socket aktiv, Vision-Sampling, Webhook-Verarbeitung — aber mit **dynamischem** FPS bzw. Poll-Intervall proportional zu V (und umgekehrt Backoff bei Überlast).
- **Traum-Phase (hohe R, gesenktes externes Sampling):** HA-Verbindung kann auf **Long-Poll** oder **gepufferte Pulls** wechseln; Haupt-CPU für **Void-Scans**, Graph-Heuristiken über Chroma, **Selbst-Fragegenerierung** und kontrollierte OpenClaw-Aufrufe.
- **Übergänge** werden durch **Entropie- und Last-Signale** gesteuert: z. B. Shannon-Approximation der Event-Rate, Queue-Tiefe, OpenClaw-„busy“-Flag — alles in Float-Features, die in eine **weiche** Entscheidungsfunktion (Sigmoid mit Λ-Offset, kein harter 0.5-Schnitt) einfließen.

Optional: zwei **physische** Threads/Prozesse („Kortex“ getrennt von „Hirnstamm“), aber **eine** autoritative Pacemaker-Quelle, um Split-Brain zu vermeiden.

### Sentinel in diesem Modell

Sentinel ist **nicht** statisch „immer an“ mit fester Rate, sondern **amplitudenmoduliert**: bei niedrigem V werden nur **kritische** Entity-Changes (Allowlist) noch in Echtzeit verarbeitet, der Rest in Batch.

### Traumschleife in diesem Modell

Void Detection ist die **dominante kognitive Arbeit** in Traum-Phasen; Output (Void-Tickets) kann die nächste Wach-Phase **prägen** (welche HA-Topics stärker indexiert werden).

### Vor- und Nachteile

| Kriterium | Einschätzung |
|-----------|--------------|
| **A7** | **Pro:** Explizites Modell „was tun wir gerade“ erleichtert **Audit** („Warum wurde Event X verzögert?“ → Traum-Phase + dokumentierte Policy). **Contra:** **Komplexere** Erklärbarkeit für externe Auditor:innen; dynamische Drosselung darf nicht als **stilles Drop** missverstanden werden — jedes Abwürgen braucht **A7-konforme** Spur (Grund: `phase=R`, `entropy_epsilon`, Policy-ID). |
| **A6** | **Pro:** **Natürliche Heimat** für Float-Zustände (V, R, Prioritäten, Schwellen mit Λ). **Contra:** Gefahr, Phasen intern doch als **Int-Enum** zu kodieren — dann bricht die Isomorphie zur Resonanzdomäne; Implementierung muss Phasen als **kontinuierliche Mischkoeffizienten** modellieren oder klar als abgeleitete Observables aus Floats dokumentieren. |
| **Latenz** | **Pro:** Unter Last **automatische** Priorisierung — kritische Signale können V anheben und Traum unterbrechen. **Contra:** In Traum-Phase **höhere** maximale Latenz für weniger kritische HA-Events; muss mit Operator-Erwartung und HA-SLA abgestimmt werden. |
| **OMEGA** | **Pro:** Starke narrative und technische Passung zu **5-Phasen-Engine**, **Takt/W-Takt**, und zur Ticket-12-Forderung, **Idle-Lernen** mit **Apoptose** zu **ko-schedulen** — Traum und „Zelltod“ sind beide **Wartungsmodi** mit unterschiedlicher Zielrichtung. **Contra:** Höchster **Engineering-Aufwand** für Stabilität (Oscillation zwischen Phasen, Hysterese, Anti-Flapping). |

---

## Kurzvergleich (Entscheidungshilfe)

| Aspekt | Monolith (1) | Event/Push (2) | Schlaf-Wach (3) |
|--------|----------------|----------------|-----------------|
| Betriebskomplexität | niedrig | hoch | mittel–hoch |
| A7-Auditpfad | einfach lokal, aber SPOF | viele Kanten, stärker segmentiert | gut erklärbar, aber viele Parameter |
| A6-Treue | gut, Disziplin nötig | gut, Schema-Disziplin nötig | sehr gut (wenn konsequent Float) |
| Latenz HA-Ingest | niedrig (wenn Loop sauber) | sehr niedrig am Ingress | variabel (phasenabhängig) |
| Skalierung / Team-Schnitt | schwächer | stärker | mittel |

---

## Empfehlung für das Umsetzungs-Ticket (kein Bindungsbeschluss)

Die drei Konzepte sind **orthogonal genug**, um **hybrid** zu werden (z. B. Monolith für Sentinel + separater Queue-Ingress nur für HA; oder Pacemaker aus Konzept 3 über Konzept 2 steuern). Die offenen Punkte aus Ticket 12 §5 (Queue-Wahl, Idempotenz, OpenClaw „ein Prozess vs. Sidecar“) sollten **nach** Pilotmessungen (reale Event-Rate, VPS-CPU, Chroma-Größe) entschieden werden — mit **harter** A7-Protokollierung für jeden Drop und **durchgängigen** Floats für Steuergrößen (A6).

---

*Ende Dokument — bereit für O2-Audit und Auswahl/Hybridisierung.*
