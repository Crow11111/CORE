# System-Architektur Spezifikation: ATLAS Neocortex V1.0

**Status:** Verbindliche, persistente System-Direktive. Im Workspace von OC Brain hinterlegt.

**Schnittstellen & Kanäle:** Siehe `ATLAS_SCHNITTSTELLEN_UND_KANAALE.md` (im Repo: docs/02_ARCHITECTURE/) – Dreadnought↔OC Brain, Scout-Webhook, WhatsApp, ChromaDB, .env-Checkliste.

Analyse der Direktiven und Constraints wurde abgeschlossen. Die folgende Spezifikation definiert die initiale Architektur zur Erreichung der gesetzten Ziele.

---

## 1. Topologie & Failover-Prozess (Sensor-Trigger bei Dreadnought OFF)

Szenario: Die Kamera Tapo C52A detektiert eine Bewegung. Dreadnought ist offline.

### Sensor → Scout (Lokales Nervensystem)

- Tapo C52A sendet Event (Momentaufnahme/Clip) via MQTT an lokalen Broker auf Scout (Raspi 5).
- Scout: lightweight Pre-Processing (HA oder Python). **Triage:** Nacht? Safe state (Marc zuhause)? Repetitives Ereignis?
- Wenn nicht trivial → Eskalation.

### Scout → OC Brain (Cortex)

- Scout sendet HTTPS Webhook (POST) an definierten Endpunkt des OC Brain (VPS).
- **Payload (JSON):**
```json
{
  "source": "scout",
  "node_id": "raspi5-ha-master",
  "event_type": "motion_detected_prefiltered",
  "timestamp": "2026-02-28T15:00:00Z",
  "priority": "medium",
  "data": {
    "device": "tapo_c52a",
    "snapshot_url_local": "http://192.168.1.X/snapshot.jpg"
  }
}
```

### OC Brain (Logik & Entscheidung)

- Brain prüft `dreadnought_status` → OFFLINE.
- **Logik-Pfad A (Dreadnought OFFLINE):**
  - Event in relationalem State + ChromaDB loggen (`dreadnought_pending`).
  - Eskalation an Pilot: WhatsApp `[ATLAS-ALERT] Motion detected (Tapo C52A). Dreadnought offline. Review required? [Yes/No]`
  - Task-Queuing: Event in persistente Warteschlange für Dreadnought; Abarbeitung wenn Dreadnought online.

---

## 2. Protokolle & Schnittstellen

| Strecke | Protokoll | Port | Anmerkung |
|--------|-----------|------|-----------|
| Sensoren ↔ Scout | MQTT | 1883 | Lokal, hocheffizient |
| Scout ↔ OC Brain | HTTPS (Webhook) | 443 | Nginx Reverse Proxy, zustandslos |
| OC Brain ↔ WhatsApp | HTTPS REST | 443 | message-Tool |
| OC Brain ↔ ChromaDB | TCP (Docker-intern) | 8000 | Semantischer Speicher |
| OC Brain ↔ Dreadnought | HTTPS REST | — | Dreadnought pollt (vermeidet Timeouts bei OFF) |

---

## 3. Datenstruktur (ChromaDB & Relationaler State)

### A) ChromaDB

- **Collection `events`:** Embeddings von Sensor-Daten. Metadaten: `timestamp`, `source_device`, `event_type`, `priority`, `processed_by`, `analysis_pending`.
- **Collection `insights`:** Destillierte Erkenntnisse, Kausal-Ketten. Metadaten: `confidence_score`, `source_event_ids`, `user_feedback`.

### B) Relationaler State (SQLite/PostgreSQL auf VPS)

- **Tabelle `node_status`:** `node_id`, `status`, `last_heartbeat`.
- **Tabelle `action_log`:** `action_id`, `timestamp`, `source_event_id`, `decision_logic_used`, `action_taken`, `predicted_outcome_vector`, `actual_outcome_vector`, `feedback_score` (Kern der prädiktiven Matrix).

---

## 4. Rekursive Iterations-Engine (Evolutions-Loop)

### Phase 1: Entropie-Detektion

- Passive Trigger: Latenz > 500ms, CPU > 80 %, etc.
- Aktive Trigger: Exception, negatives User-Feedback (`feedback_score < 0`), explizite Direktive von Marc.

### Phase 2: Analyse & Hypothesenbildung

- Brain isoliert Problem, korreliert `action_log` und `node_status`.
- Beispiel-Hypothesen: Software-Flaschenhals (z.B. OpenCV auf CPU), Docker-Ressourcen-Limits.

### Phase 3: Autonome Recherche & Lösungs-Generierung

- Sub-Agent mit Direktive (z.B. „Recherchiere Optimierungsmöglichkeiten für Objekterkennung auf 4-vCPU Docker“).
- Priorisierte Liste: Software-Refactoring vs. Hardware (z.B. Coral TPU).

### Phase 4: Entscheidung & Exekution

- **Software:** Refactoring, Test-Deploy.
- **Hardware-Eskalation:** Wenn physikalisches Limit erreicht → **Evolution Request** an Marc:
  - Format: `[ATLAS EVOLUTION REQUEST]` mit Analyse, Limit, Forderung, Empfehlung (z.B. Google Coral USB), Begründung, erforderliche Aktion.

Das System betrachtet die Überwindung eigener Grenzen als Kernfunktion.
