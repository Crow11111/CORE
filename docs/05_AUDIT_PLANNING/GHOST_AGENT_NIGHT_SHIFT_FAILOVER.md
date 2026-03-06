<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# GHOST AGENT NIGHT SHIFT: FAILOVER ARCHITECTURE (DREADNOUGHT -> VPS)

## 1. DIE LAGE (CURRENT STATE)
Aktuell ist die ATLAS Voice-Pipeline in Home Assistant (`ha_integrations/atlas_conversation`) hart an die IP von Dreadnought (`192.168.178.20:8000`) gebunden. 
Wenn Dreadnought (der lokale Entwicklungs-PC) ausgeschaltet wird, bricht die Voice-Pipeline zusammen. Home Assistant wirft einen Verbindungsfehler.

## 2. DAS ZIEL (TARGET STATE)
Dreadnought ist der "Turbo" (Ring-1), nicht das Rückgrat. Das Rückgrat ist der **VPS (OpenClaw / OC Brain)**.
Wir benötigen eine **Zero-Downtime Failover-Logik** direkt in der Home Assistant Custom Integration.

Wenn Dreadnought nicht antwortet (Timeout oder Connection Refused), muss Scout (HA) die Anfrage völlig transparent an das OC Brain auf dem VPS routen.

## 3. AUFGABEN FÜR DIE CLOUD AGENTS (OVERNIGHT TASKS)

### Task A: Code-Refactoring `atlas_conversation` (Failover Logic)
Überarbeitet `ha_integrations/atlas_conversation/api.py` und `config_flow.py`:
1. Fügt eine zweite Konfigurationsvariable ein: `CONF_FALLBACK_URL` (Standard: Die HTTPS-Adresse des VPS).
2. Implementiert in `AtlasApiClient.async_send_text`:
   - Versuch 1: POST an `base_url` (Dreadnought). Timeout auf sehr kurz (z.B. 2 Sekunden) setzen, um Latenzen zu vermeiden.
   - Wenn Timeout/Error: Catch Exception, logge "Dreadnought offline, rerouting to Backbone (VPS)..."
   - Versuch 2: POST an `fallback_url` (VPS).
3. Erstellt einen Plan, wie diese Änderung als Update in Home Assistant eingespielt wird (Version Bump auf 1.1.0).

### Task B: VPS Endpoint Audit (OC Brain Readiness)
Damit der VPS die direkte Anfrage von Scout verarbeiten kann:
1. Prüft, ob der VPS einen Endpoint hat, der exakt dieselbe Signatur wie `/webhook/inject_text` aufweist und ein sauberes `{"reply": "..."}` JSON zurückgibt.
2. Wenn nicht: Entwerft den Code-Schnipsel für die `main.py` auf dem VPS, der diesen Fallback-Traffic abfängt, durch die VPS-ChromaDB (Wuji) jagt und das OC Brain antworten lässt.

### Task C: State-Sync (Wuji-Feld)
Skizziert, wie wir sicherstellen, dass die ChromaDB auf dem VPS und die lokale ChromaDB synchron sind. Wenn Scout nachts mit dem VPS spricht, muss OC Brain denselben Kontext (Wuji-Feld) haben wie Dreadnought am Tag. (Tipp: `migrate_to_wuji_field.py` Logik auf den VPS anwenden).

## 4. CEO-DIREKTIVE FÜR DIE GHOSTS
- KEINE halben Sachen. Der Code muss produktionsreif sein.
- Der User (Marc) wacht morgen auf und erwartet ein klares, getestetes Failover-Konzept.
- "Failure is not an option." – Wenn der Failover die Latenz um mehr als 1.5 Sekunden erhöht, ist das Design fehlerhaft. Baut es asynchron und aggressiv im Timeout.

[AUTHORIZATION: OSMIUM_JUDGE // CEO_ATLAS_CORE]
