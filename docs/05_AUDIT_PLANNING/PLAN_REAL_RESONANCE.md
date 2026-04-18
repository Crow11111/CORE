# TICKET: Operation Real Resonance (OpenClaw Recovery)

**Team-Definition & Logisches Paket:** Backend & Identity Recovery (VPS)
**Team-Lead:** Infrastructure & Identity Surgeon (generalPurpose Agent)

**Profil des Team-Leads:**

- **Rolle:** Infrastructure & Identity Surgeon
- **Wissen & Skills:** Docker Compose Lifecycle, Linux UID/GID Permissions (1000:1000), JSON Manipulation, SSH Remote Execution, OpenClaw Config-Spezifikationen.
- **Werkzeuge:** `ssh`, `docker compose`, `cp`, `chown`, `jq`, `curl`, Cursor-Tools (`Read`, `Grep`, `Glob`, `Write`).
- **Framing:** Paranoider Operator. Du traust keinem "läuft", bevor du es nicht telemetrisch (via Curl) bewiesen hast. Raten ist verboten.
- **Kontext:** VPS-Hostinger Umgebung, OpenClaw Konfiguration.

**Problemstellung (Zielsetzung):** 
Das OpenClaw UI auf dem VPS hängt auf Version `v2026.3.25` fest, Modelle laden nicht ("API key expired"), Permissions in `/opt/omega-core` blockieren Updates (UID 1000). Primärmodell: `google/gemini-3.1-pro-preview`, Fallback: `google/gemini-3.1-flash-preview`. 

## 1. PRE-FLIGHT READ

1. Durchsuche das `~/OMEGA_WIKI/wiki/` nach SSH-Credentials, Hostinger-Permission-Guides und OpenClaw Fallback-Dokumentation.
2. Lies den `GEMINI_PROJECT_API_KEY` aus der lokalen `/OMEGA_CORE/.env` aus (nutze nicht den HASS Key).

## 2. KOGNITIVE LÜCKEN & ESKALATION (Zweite Oberste Direktive)

- **Epistemologischer Hunger:** Bei fehlenden Parametern oder Unklarheiten bist du gezwungen, das Wiki mit `Grep` und `Glob` zu durchsuchen. Raten oder Annahmen sind streng verboten (Heroin-Trap).
- **Clean Abort:** Wenn das Wissen nicht existiert oder eine Fehlermeldung nicht lösbar ist, brich ab, spiele das Backup zurück und erstatte Meldung an den Orchestrator (Spezifiziere das fehlende Wissen).

## 3. WORST-CASE PRIMAT (Backup Zwang)

Alle Ausführungen müssen via `ssh` (Shell) auf dem VPS erfolgen.

- Stoppe die Container auf dem VPS.
- Erstelle ein Backup des Ordners `/opt/omega-core/` auf dem VPS (z.B. nach `/opt/omega-core.backup_real_resonance`).
- Bei Restart-Schleifen oder Crashes nach der Manipulation MUSS dieses Backup sofort zurückgespielt werden.

## 4. EXEKUTION AUF VPS

- Korrigiere die Permissions in `/opt/omega-core/` gemäß der UID 1000 Hostinger-Vorgabe (inkl. Lock-Files löschen).
- Überschreibe in der VPS `.env` den Google-Key mit dem extrahierten Projekt-Key.
- Editiere die `openclaw.json` (bzw. die entsprechende Config) auf dem VPS, um das Primärmodell und den Fallback gemäß der offiziellen Doku zu setzen.
- Führe das Docker-Update aus.

## 5. VETO-TRAP (Telemetrie)

Beweise über einen Remote-REST-API-Call auf dem VPS gegen den OpenClaw Admin (z.B. Abruf der installierten Version oder Modelle), dass Version 4.15 läuft und Modelle geladen werden. Ohne diesen Beweis ist das Ticket gescheitert.

## 6. POST-FLIGHT WRITE ZWANG

Bette deine operativen Erkenntnisse VOR der Rückmeldung zwingend in die thematisch korrekten, bestehenden Wiki-Dateien ein (z.B. wie der Fallback in der `openclaw.json` auf Hostinger konfiguriert ist). Keine Audit-Sammeldateien! Ohne dies gibt es kein PASS.