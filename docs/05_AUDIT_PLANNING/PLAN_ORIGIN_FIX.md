# TICKET: Operation Open Border (Origin Fix)
# VECTOR: 2210 | DELTA: 0.049

**Team-Definition & Logisches Paket:** Security & CORS Alignment
**Team-Leads:** Security Engineer & Network Architect (generalPurpose Agent)

**Profil des Teams:**
- **Rolle:** Security Engineer & Network Architect
- **Wissen & Skills:** OpenClaw Security Model (Allowed Origins), CORS, Reverse Proxy Headers, JSON Configuration.
- **Werkzeuge:** `ssh`, `docker`, `curl`, `jq`, `Read`, `Grep`, `Glob`, `Write`.
- **Framing:** Paranoia vs. Usability. Du öffnest die Grenze präzise für den legitimen Host, ohne die Sicherheit zu untergraben.
- **Kontext:** Wiki (`OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md`), VPS-Konfiguration (`/opt/openclaw/data/openclaw.json`).

**Problemstellung (Zielsetzung):**
Der Login in die OpenClaw UI schlägt fehl mit der Meldung: "origin not allowed (open the Control UI from the gateway host or allow it in gateway.controlUi.allowedOrigins)". Dies liegt daran, dass der Browser die Anfrage von `http://187.77.68.250:32776` sendet, OpenClaw dies aber nicht als legitimen Ursprung erkennt.

## 1. PRE-FLIGHT (Diagnose)
1. Verbinde dich per SSH auf den VPS.
2. Lies die aktuelle `openclaw.json` aus. Suche nach `allowedOrigins`.
3. Prüfe, ob in der OpenClaw-Konfiguration bereits `allowedOrigins` existiert und was dort eingetragen ist.

## 2. EXEKUTION (Security Patch)
1. **OpenClaw Config:** Editiere die `openclaw.json` auf dem VPS.
   - Füge unter `gateway.controlUi` das Feld `allowedOrigins` hinzu (falls fehlend) oder erweitere es.
   - Trage dort den exakten Ursprung ein: `["http://187.77.68.250:32776"]`.
2. **Restart:** Starte den OpenClaw Container neu.

## 3. WORST-CASE PRIMAT (Ersatzpfade)
- Sollte der Fehler weiterhin bestehen, versuche zusätzlich `"*"` als Test-Origin (nur kurzzeitig zur Verifikation, dann wieder einschränken).
- Prüfe, ob `gateway.controlUi.allowedOrigins` im Schema der v4.16 eventuell anders strukturiert ist.

## 4. VETO-TRAP (Beweis)
Der Worker darf erst Vollzug melden, wenn er telemetrisch (z.B. durch einen Login-Versuch via `curl` mit Origin-Header) beweisen kann, dass der Server die Anfrage nicht mehr mit "origin not allowed" ablehnt.

## 5. POST-FLIGHT WRITE (Alignment)
1. Aktualisiere `/OMEGA_CORE/src/scripts/deploy_vps_full_stack.py`, damit `allowedOrigins` in die generierte Konfiguration aufgenommen wird.
2. Dokumentiere den Parameter in `OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md` im Wiki.
3. Melde jede Abweichung. No Diary!