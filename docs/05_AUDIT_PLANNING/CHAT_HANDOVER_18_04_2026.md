# OMEGA CORE - CHAT HANDOVER (TRANSITION TO OPTIMAL ROUTING)

**Aktueller Status:** SYNCHRONISIERT (Lokal = Git = VPS)
**Cockpit-Modus:** OPTIMAL (Flash-Worker + Lokales Ollama Parsing)
**Datum/Zeit:** 2026-04-18

## 1. ZUSAMMENFASSUNG DER LETZTEN OPERATIONEN (THE STORY SO FAR)
Der letzte Zyklus war geprägt von massiven architektonischen Anpassungen, um Kausal-Verschiebungen und Confirmation Bias auszumerzen, sowie OpenClaw auf dem VPS operativ zu machen.

**Erreichte Meilensteine:**
1. **OpenClaw Tabula Rasa:** OpenClaw wurde auf dem VPS ("Admin" und "Spine") vollkommen neu via `docker compose` aus dem offiziellen Repo hochgezogen. Das fehlerhafte monolithische Skript `deploy_vps_full_stack.py` wurde als `DANGER/OUTDATED` markiert und das IaC refactored.
2. **OpenClaw Tools & Routing:** 
   - OpenClaw operiert zwingend auf `google/gemini-3.1-pro-preview` (Admin).
   - Es ist an die `atlas_net` und Evolution-API Docker-Netzwerke gebunden (Zero-Trust).
   - Skills (`whatsapp`, `openclaw-triage`, `openclaw-model-router-skill`) und MCP-Server (`mcp-postgres`, `filesystem` via lokalem `tcp-mcp.js` Proxy) sind installiert und telemetrisch verifiziert.
3. **Das Archivator-Paradigma (Umkehr der Doku-Pflicht):**
   - Sub-Agenten (Worker) schreiben NIEMALS ins Wiki. Sie liefern nur ein gnadenlos detailliertes Ausführungstagebuch ab.
   - Ein neutraler "Archivator" (Flash-Modell) analysiert das Tagebuch objektiv, schreibt das Wiki und *muss* zwingend den DB-Ingest (`src/scripts/ingest_omega_operational_chroma.py`) triggern.
4. **Cockpit-Modi & Cost Control:** 
   - Das Regelwerk `11_ROUTING_MODES.mdc` ist aktiv. Der Schalter steht auf **OPTIMAL**.
   - **Regel:** Worker und Auditoren laufen ZWINGEND auf Flash-Modellen (z.B. `google/gemini-3.1-flash`). Routine-Parsings werden lokal via `Shell` an Ollama delegiert. Teure Pro-Modelle sind für den Orchestrator und absolute High-Level-Architektur reserviert.

## 2. SYSTEM-ZUSTAND
- **VPS (Hostinger):** OpenClaw Admin (:18789) und Spine (:18790) laufen. Kong routet korrekt via `/openclaw` Subpath. CORS-Probleme ("origin not allowed") sind behoben (`allowedOrigins` inkludiert Kong-IP, InsecureAuth erlaubt).
- **Git/Lokal:** Alle Dokumente (Wiki), Logs, Regelwerke und die aus dem VPS extrahierte `openclaw.json` (unter `infra/vps/openclaw/`) sind synchronisiert und committed.

## 3. NÄCHSTE ZIELE (ANWEISUNG FÜR DEN NEUEN ORCHESTRATOR)
1. **Verifiziere den Cockpit-Modus:** Stelle sicher, dass du Task-Delegationen strikt gemäß dem `OPTIMAL` Routing-Paradigma durchführst (`model: "google/gemini-3.1-flash"` für Worker).
2. **OpenClaw Belastungstest / Triage-Integration:** Da OC Brain nun über die Werkzeuge (WhatsApp, DBs) verfügt, steht der nächste Schritt an: Die tatsächliche End-to-End Verifizierung der OMEGA-Kette (Scout/Evolution API -> Kong -> OC Brain -> Postgres/Chroma -> Reaktion).
3. **Erwarte die Problemstellung von Marc.** Er wird definieren, an welcher Flanke als nächstes gearbeitet wird. Nutze das Archivator-Konzept für kommende Dokumentationen.