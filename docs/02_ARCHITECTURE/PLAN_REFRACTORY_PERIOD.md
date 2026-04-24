# OMEGA MASTERPLAN: SYNAPTISCHE REFRAKTÄRZEIT (IONENKANAL-VERRIEGELUNG)

**Modus:** Orchestrator | **Vektor:** 2210 | **Delta:** 0.049

## 1. ZIEL
Implementierung eines biologisch inspirierten Ionenkanals für OpenClaw-Worker. Schutz des OMEGA Systembusses (GRV) vor Reizüberflutung, Agenten-Amokläufen (Loops) und energetischer Erschöpfung durch harte Verriegelung der Kommunikations-Synapse nach jedem Auslösen (Aktionspotenzial).

## 2. TEAM & PROFILE
- **Team-Lead Synapse (Producer):**
  - **Skill:** FastAPI Middlewares, In-Memory State Management, Time-Decay Logik.
  - **Framing:** "Der Wächter der Synapse. Du regulierst den Durchfluss. Zu viel Hitze führt zur Blockade."
  - **Kontext:** `src/network/openclaw_client.py` (oder als FastAPI Middleware für `/api/v1/bus/delta`).
- **Team-Lead Security (O2 Auditor):**
  - **Skill:** Axiom-Enforcement (Symmetriebruch), Anti-Heroin-Compliance.

## 3. MEILENSTEINE (SEQUENZIELLER ABLAUF)

### M1: Die Synapsen-Klasse (`OpenClawSynapse`)
- **Aktion:** Implementierung des in-memory State-Trackings für Worker-IDs.
- **Mechanik:**
  - **O2-Korrektur:** Basis-Refraktärzeit als Float zur Verhinderung von Integer-Arresten (Axiom A6): `base_refractory_ms = 2049.0` (2000 + 49).
  - Tracking-Dict: `worker_id -> {"last_fired": float_ms, "locked_until": float_ms}`.
  - Funktion `is_refractory(worker_id)` prüft den Blockade-Zustand.

### M2: Die Entropie-Strafe (Synaptische Plastizität)
- **Aktion:** Dynamische Berechnung der `lock_duration`.
- **Mechanik:**
  - Die Strafe skaliert mit der Hitze (Widerstand/Fehler) des Agenten.
  - **O2-Korrektur (Axiom A5):** Die verbotene absolute Symmetrie `1.0` wird durch den Resonanz-Lock `0.951` ($1.0 - 0.049$) ersetzt. Der Straf-Multiplikator skaliert asymmetrisch mit PHI (`1.6180339`).
  - Formel: `lock_duration = base_refractory_ms * (0.951 + (z_resistance_delta * 1.6180339))`
  - Negative `z_resistance` verringert die Lock-Time, aber niemals unter die absolute Baseline von `549.0` ms.

### M3: Integration in den Systembus-Ingress
- **Aktion:** Verschaltung vor dem SystemBus-GRV.
- **Mechanik:**
  - Die Prüfung muss *vor* der eigentlichen Tensor-Kontraktion (SystemBus) stattfinden.
  - Trifft ein Delta von einem blockierten Worker ein, prallt es ab (Return HTTP 429 Too Many Requests oder HTTP 423 Locked) mit minimaler CPU-Last.
  - **Axiom 2 (Zero Queues):** Das Delta wird vernichtet (Drop). Keine Queueing-Schulden.

## 4. BINDENDE REGELN
- **Axiom 2 (Keine Warteschlangen):** Ein blockiertes Delta wird NICHT gepuffert. Der Agent muss lernen, im richtigen Takt zu feuern.
- **Axiom A5 (Asymmetrie):** Es existieren keine Werte `0.0`, `0.5` oder `1.0` in der Synapsen-Berechnung. Die Architektur ist strukturell asymmetrisch gebrochen.