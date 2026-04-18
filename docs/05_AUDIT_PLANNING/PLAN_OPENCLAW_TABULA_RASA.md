# TICKET: Operation Tabula Rasa (OpenClaw Hostinger Re-Install)

**Team-Definition & Logisches Paket:** Infrastructure & Setup Recovery
**Team-Lead:** Setup & Teardown Surgeon (generalPurpose Agent)

**Profil des Team-Leads:**
- **Rolle:** Setup & Teardown Surgeon
- **Wissen & Skills:** Offizielle Hostinger Docker Deployments, OpenClaw Architektur, Bash/SSH, Reverse Proxy Connectivity.
- **Domäne & Toolkit:** Voller Zugriff auf IDE-Tools (Read, Write, Grep, Glob) und VPS-Shell (SSH). Du wählst eigenverantwortlich die effizientesten Werkzeuge innerhalb dieser Domäne, um das Problem zu lösen.
- **Framing:** Tabula Rasa Operator. Du vertraust nur dem offiziellen Vendor-Code. Du dokumentierst jede Abweichung für den Wissensgewinn.

**Problemstellung (Zielsetzung):**
Die aktuelle OpenClaw-Instanz unter `/opt/omega-core/openclaw-admin` ist eine unsaubere Manuell-Installation. Ziel ist ein radikaler Neuanfang nach offiziellen Vorgaben (Hostinger/OpenClaw), bei dem unsere OMEGA-Netzwerk-Routen erhalten bleiben.

## 1. PRE-FLIGHT (Informationsbeschaffung)
Erkunde das Wiki (`/home/mth/OMEGA_WIKI/wiki/`) und die lokale `.env`, um alle nötigen Parameter (SSH, Keys, Ports, offizielle Setup-URLs) selbstständig zu identifizieren. Sollten kritische Infos fehlen: BRICH AB und melde die Lücke.

## 2. EXEKUTION (Teardown & Rebuild)
1. **Teardown:** Stoppe die unsaubere Installation in `/opt/omega-core/` und isoliere den Ordner. Fasse die aktiven Atlas-DBs (`/opt/atlas/`) NIEMALS an.
2. **Rebuild:** Installiere OpenClaw nach dem offiziellen Standard-Verfahren (Git URL und Setup-Skript findest du in der offiziellen Doku im Wiki). Sorge dafür, dass OpenClaw an `127.0.0.1:18789` gebunden wird.
3. **Konfiguration:** Nutze den `GEMINI_PROJECT_API_KEY` und generiere ein sicheres Gateway-Token.

## 3. ABWEICHUNGS-MELDEPFLICHT & ESKALATION
- Sollte das Setup-Skript interaktive Eingaben fordern oder die Architektur (Pfade/Ports) von den Wiki-Vorgaben abweichen, MUSST du dies detailliert melden. Dies gilt als wertvoller Wissensgewinn.

## 4. VETO-TRAP (Beweis)
Weise telemetrisch (via Curl/Docker-Logs) nach, dass die UI erreichbar ist und die kritischen OMEGA-Datenbanken (Atlas) unberührt geblieben sind.