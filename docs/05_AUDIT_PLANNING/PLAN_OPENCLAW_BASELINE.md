# TICKET: OpenClaw Baseline Configuration & Bootstrap

**Team-Definition & Logisches Paket:** System Initialization & Bootstrap
**Team-Lead:** OpenClaw Bootstrap Expert (generalPurpose Agent)

**Profil des Team-Leads:**

- **Rolle:** OpenClaw Bootstrap Expert
- **Wissen & Skills:** OpenClaw Workspace Initialisierung, Bootstrap-Prozesse, JSON/Markdown Config-Injection, Hostinger VPS Setup.
- **Domäne & Toolkit:** Voller Zugriff auf IDE-Tools und VPS-Shell (SSH). Browser-Tooling falls UI-Interaktion nötig ist.
- **Framing:** Der Agent ist gefangen im "Bootstrap pending" Zustand. Du musst die Initialisierung abschließen und das Gehirn auf das richtige Modell (3.1 Pro) eichen.
- **Kontext:** OMEGA Axiome (`OMEGA_AXIOME.md`), `OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md`, VPS Dateisystem.

**Relevante Axiome:**

- **Axiom 7 (Zero-Trust):** Verifizieren statt glauben. Raten beim Bootstrap ist verboten.
- **Zweite Oberste Direktive:** Epistemologischer Hunger bei Wissenslücken.

**Problemstellung (Zielsetzung):**
Die neu aufgesetzte OpenClaw Instanz auf dem VPS weigert sich zu arbeiten. Das UI zeigt den Fehler: `[Bootstrap pending] Please read BOOTSTRAP.md from the workspace and follow it before replying normally.` Zudem ist das Primärmodell fälschlicherweise auf `Gemini 2.5 Pro` zurückgefallen. 

## 1. PRE-FLIGHT (Informationsbeschaffung)

Lies die offiziellen Dokumentationen unter `https://docs.openclaw.ai/` und `https://www.hostinger.com/support/how-to-install-openclaw-on-hostinger-vps/` (via WebSearch/WebFetch), um zu verstehen, was OpenClaw bei einem Bootstrap erwartet. Führe zwingend einen Pre-Flight Read der existierenden Dokumentation (z.B. in `~/OMEGA_WIKI/wiki/` oder `docs/`) durch.

**[MCP PRE-FLIGHT RESULTS / GAPS]**

- **Gaps:** "VPS-Host MCP-HTTP (Port 8001) nicht erreichbar — Remote-Tooling ggf. down." Dies betrifft den OMEGA MCP Server, nicht OpenClaw selbst, zeigt aber allgemeine Netzwerk-/Docker-Zustände auf.
- **Recommendations:** "Prüfen: `verify_vps_stack`, Docker `mcp-server`, UFW." Falls du bei OpenClaw auf Netzwerkprobleme stößt, beachte dies.

## 2. EXEKUTION (Bootstrap & Modell-Eichung)

Löse das "Bootstrap pending" Problem gemäß der offiziellen Dokumentation und der `BOOTSTRAP.md` im Workspace des VPS (`/opt/openclaw/data/workspace/` oder ähnlich). Sorge zudem dafür, dass das Modell hart auf `google/gemini-3.1-pro-preview` eingestellt wird. Nutze dafür die Domäne der Shell/SSH und deiner IDE-Tools, entscheide den genauen Lösungsweg selbst.

## 3. WORST-CASE PRIMAT & ESKALATION

- **Backup:** Vor jeglicher Änderung im Workspace-Verzeichnis auf dem VPS ist ein Backup des Verzeichnisses via SSH zu erstellen.
- **Eskalation / Clean Abort:** Solltest du die `BOOTSTRAP.md` nicht finden, den Prozess nicht automatisieren können oder Fehler auftreten: BRICH AB, spiele das Backup zurück und melde die genaue Blockade an den Orchestrator (Epistemologischer Hunger). Kein Raten!

## 4. VETO-TRAP (Beweis)

Weise telemetrisch (via Docker Logs oder Curl gegen die interne API `127.0.0.1:18789` via SSH) nach, dass der Zustand "Bootstrap pending" aufgehoben ist und das Modell 3.1 Pro geladen wurde.

## 5. POST-FLIGHT WRITE ZWANG

Bette deine gewonnenen Fakten (Wie genau löst man den Bootstrap? Wo stellt man das Modell ein?) VOR der Rückmeldung zwingend in die thematisch korrekte Datei `OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md` im Wiki ein. Keine Tagebücher! Ohne dies gibt es kein PASS.
**WICHTIG (Datei-Hygiene):** Wenn du eine neue Datei anlegst, musst du sie sofort im `docs/00_STAMMDOKUMENTE/CORE_INVENTORY_REGISTER.md` registrieren.
Trage den Abschluss dieser Aufgabe zwingend in das aktuelle Session-Log unter `docs/05_AUDIT_PLANNING/` ein.