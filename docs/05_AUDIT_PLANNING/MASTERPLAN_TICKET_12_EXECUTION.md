# MASTERPLAN: TICKET 12 EXECUTION (EPISTEMIC DRIVE)

**Vector:** 2210 (Execution) | **Status:** ACTIVE
**Orchestrator:** Ring 0 (OMEGA)
**Ziel:** Physische Implementierung der Hybrid-Spezifikation (Ticket 12) für den autonomen Sentinel-Daemon und die Traumschleife auf dem VPS.

## PHASE 1: INGEST PERIMETER & QUEUE (VPS)
**Team Lead:** Infrastructure & DB Architect
**Ziele:**
1. **Event-Queue:** Einrichtung einer Queue auf dem VPS (um zusätzliche Container wie Redis/RabbitMQ zu vermeiden, nutzen wir PostgreSQL mit `FOR UPDATE SKIP LOCKED` als robuste, transaktionale Queue-Tabelle `omega_ingest_queue`).
2. **Normalisierungs-Client:** Erstellung eines Clients (`src/db/ingest_queue_client.py`), der Roh-Events aus der Queue zieht, dedupliziert (Idempotenz) und als formal validierte Events in den bestehenden `omega_events` Store (aus Ticket 11) überführt.
**Abnahme:** `pytest tests/test_ingest_queue.py` schlägt "Verification-First" Traps (Zero-Trust, Queue-Isolation) erfolgreich auf PASS um.

## PHASE 2: THE SENTINEL DAEMON (HA/VISION INBOUND)
**Team Lead:** Integration & Telemetry Specialist
**Ziele:**
1. **Sentinel (`src/daemons/vps_sentinel_daemon.py`):** Verbindet sich mit Home Assistant (via Long-Poll/WebSocket) und/oder nimmt Vision-Anker entgegen.
2. **Pacemaker-Kopplung:** Der Sentinel drosselt oder erhöht seine Sampling-Rate anhand des lokalen Pacemakers (Vigilanz $V$ / Ruhe $R$).
3. **Isolierter Push:** Der Sentinel schreibt ausschließlich in die `omega_ingest_queue`, niemals direkt in die `omega_events` Historie oder an OpenClaw.
**Abnahme:** Der Daemon läuft isoliert und legt bei simulierten HA-Events erfolgreich strukturierte Payloads in die Queue ab.

## PHASE 3: TOPOLOGICAL VOID DETECTION & SYNTHESIS (THE DREAMER)
**Team Lead:** Neuromorphic Biology Expert & Core Logic
**Ziele:**
1. **Dream Worker (`src/daemons/vps_dream_worker.py`):** Wird nur bei hoher Ruhe ($R$) und System-Idle aktiv.
2. **Void Detection:** Führt Cluster-Analysen über ChromaDB / Postgres aus, um logische Lücken (Voids) zu identifizieren und als "Void-Tickets" (`priority_float`) in eine Job-Liste zu legen.
3. **Proaktive Synthese:** Nimmt Void-Tickets, generiert epistemologische Fragen, feuert RAG-Suchen gegen OpenClaw und speichert die Antworten als neues Wissen in der ChromaDB (Grounding).
**Abnahme:** Der Dream Worker erzeugt autonom neues Wissen aus simulierten Lücken, ohne Veto-Flags zu triggern.

## PHASE 4: VOLLKREIS-AUDIT (O2)
**Team Lead:** Orchestrator B (O2 / Hugin)
**Ziele:**
1. Zero-Context Audit der Ticket 12 Implementierung.
2. Prüfung der Ingress-Auth, Float-Striktheit (A6) und Zero-Trust (A7).
**Abnahme:** O2 erteilt den finalen System-PASS.
