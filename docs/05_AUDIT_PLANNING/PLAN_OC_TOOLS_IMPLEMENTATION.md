# TICKET: OpenClaw Tool-Spezifikation & Implementierungs-Plan

**Team-Definition & Logisches Paket:** OMEGA Framework Tooling & Integration
**Team-Lead:** OpenClaw Systems Architect (generalPurpose Agent)

**Profil des Team-Leads:**

- **Rolle:** OpenClaw Systems Architect
- **Wissen & Skills:** OpenClaw CLI Tooling (ClawHub), OMEGA Framework (Kong, Evolution API, ChromaDB), LLM Routing.
- **Werkzeuge:** Voller Zugriff auf IDE-Tools, VPS-Shell (SSH) und Docker.
- **Framing:** Du agierst als leitender Architekt für die "Bewaffnung" von OpenClaw. OpenClaw hat nun ein Gehirn (Gemini 3.1 Pro), aber keine Hände (Tools). Deine Aufgabe ist es, aus den abstrahierten Anforderungen von OC Brain/OC Spine das exakte Werkzeug-Set abzuleiten und sicher zu installieren.
- **Kontext:** OMEGA Axiome, `OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md`, Session-Logs.

**Relevante Axiome & Direktiven:**

- **Zweite Oberste Direktive:** Kausal-Shift abfangen. Proaktives Handeln und Integration.
- **Axiom 7 (Zero-Trust):** Keine Tools auf dem VPS installieren, die das System kompromittieren könnten (God-Mode vermeiden).
- **Die 3-Instanzen-Workflow:** Du definierst die Befehle, überprüfst sie lokal auf Syntax-Fehler und installierst sie.

**Problemstellung (Zielsetzung):**
Basierend auf der Vor-Recherche (ClawHub, Model-Routing, Triage) muss ermittelt werden, welche Tools/Skills OpenClaw *konkret* benötigt, um als "OC Brain" (Triage, Evolution API / WhatsApp) und "OC Spine" (ChromaDB, PostgreSQL, System-Health) im OMEGA Framework agieren zu können. Diese Tools müssen in der richtigen Reihenfolge installiert und abgesichert werden.

## 1. PRE-FLIGHT (Anforderungs-Analyse)

Lies das Session Log (`docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-18.md`) und die Ergebnisse der "OpenClaw Expansion & Requirements Analysis", um zu verstehen, was zur Verfügung steht. Analysiere das OMEGA Framework (Kong, DBs, Evolution API), um abzuleiten, welche Fähigkeiten OC Brain (Messaging) und OC Spine (Daten) zwingend brauchen.

**[MCP PRE-FLIGHT RESULTS / GAPS]**

- **Gaps:** "VPS-Host MCP-HTTP (Port 8001) nicht erreichbar — Remote-Tooling ggf. down." Dies betrifft den OMEGA MCP Server. Prüfe vor der MCP-Tool-Zuweisung, ob der Endpunkt erreichbar ist.
- **Recommendations:** "Prüfen: `verify_vps_stack`, Docker `mcp-server`, UFW."

## 2. EXEKUTION (Tool-Installation & Absicherung)

**Phase 1: Abstrakte Tool-Zuweisung**
Analysiere und entscheide:

- **OC Brain (Kommunikation/Triage):** Benötigt WhatsApp-Schnittstellen (via Evolution API, also HTTP/Webhook Tools) und Model-Routing für Triage.
- **OC Spine (Persistenz/Archiv):** Benötigt MCP-Anbindungen (für ChromaDB und PostgreSQL) sowie Dateisystem-Werkzeuge für das Wiki.

**Phase 2: Reihenfolge der Installation**
Definiere die Installationsreihenfolge der Tools via OpenClaw CLI (z.B. `clawhub install ...` oder manuelle Plugin-Integration). 

1. Core-Tools (HTTP/Webhooks für Evolution API)
2. MCP-Tools (für DB-Zugriff)
3. Spezifische OMEGA-Skills (z.B. Triage-Skill).

**Phase 3: Physische Umsetzung**
Verbinde dich via SSH auf den VPS und führe die Installation der priorisierten Tools für OpenClaw im Docker-Workspace durch.

## 3. WORST-CASE PRIMAT & ESKALATION

- **Sicherheitsnetz:** Bevor ein Tool/Plugin aus einer Third-Party Quelle installiert wird, prüfe den Code/Befehl. Wenn ein Tool Abhängigkeiten fordert, die mit der Hostinger-Umgebung (Port 18789, Proxy) kollidieren, BRICH AB.
- **Clean Abort:** Wenn `clawhub` auf dem VPS nicht verfügbar ist oder Rechte fehlen, erzeuge keine Workarounds, die die Dateirechte (UID 1000) brechen. Eskaliere an den Orchestrator.

## 4. VETO-TRAP (Beweis & Abnahme)

Führe nach der Installation auf dem VPS einen API-Call gegen OpenClaw durch (z.B. über die interne API `http://127.0.0.1:18789/v1/tools` oder einen CLI-Status-Befehl), um telemetrisch nachzuweisen, dass die Werkzeuge von OpenClaw registriert und einsatzbereit sind. Liefere diesen Log an den Orchestrator zurück.

## 5. POST-FLIGHT WRITE ZWANG

Dokumentiere zwingend:

- Welche Tools exakt installiert wurden (und warum).
- In das heutige Session Log (`docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-18.md`).
- Aktualisiere die `OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md` (oder erstelle eine `OPENCLAW_TOOL_REGISTER.md`) mit den Befehlen.
(Vergiss bei neuen Dateien das Inventory Register nicht!)