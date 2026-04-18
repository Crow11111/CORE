# TICKET: Operation Glass Screen (Sub-path Asset Fix)

**Team-Definition & Logisches Paket:** Network & Application Alignment
**Team-Leads:** Network Architect & Integration Specialist (generalPurpose Agent)

**Profil des Teams:**
- **Rolle:** Network Architect & Integration Specialist
- **Wissen & Skills:** Kong Gateway Routing (Paths, Stripping), OpenClaw Gateway Configuration (basePath, trustedProxies), HTTP Header Analysis.
- **Domäne & Toolkit:** Voller Zugriff auf IDE-Tools und VPS-Shell (SSH).
- **Framing:** Der "Black Screen" ist ein Asset-Routing-Fehler. Du löst das Problem durch perfekte Synchronisation von Proxy und Applikation.
- **Kontext:** Wiki (`WEBHOOK_ARCHITEKTUR.md`, `NETZWERK_PORTS.md`, `OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md`), VPS-Dateisystem (`/opt/openclaw`), Kong Admin API.

**Problemstellung (Zielsetzung):**
Der Aufruf von `http://187.77.68.250:32776/openclaw` resultiert in einem schwarzen Bildschirm. Dies liegt daran, dass das Frontend seine Assets (JS/CSS) von der Root-Domain statt vom Unterpfad `/openclaw/` anfordert. 

## 1. PRE-FLIGHT (Diagnose)
Verifiziere den Fehler telemetrisch:
1. Rufe via SSH auf dem VPS `curl -v http://localhost:32776/openclaw` auf.
2. Analysiere im HTML-Output die Pfade zu den `<script>` und `<link>` Tags. Fordert die App `/assets/...` oder `/openclaw/assets/...` an?
3. Prüfe die aktuelle Kong-Route: Ist `strip_path` auf `true` oder `false`?

## 2. EXEKUTION (Alignment)
Ziel: OpenClaw soll wissen, dass es unter `/openclaw` lebt, und Kong soll den Pfad nicht mehr abschneiden.
1. **OpenClaw Config:** Editiere die Konfiguration auf dem VPS (wahrscheinlich `openclaw.json` oder `.env`). Setze folgende Parameter:
   - `gateway.controlUi.basePath` auf `/openclaw`
   - `trustedProxies` auf das Docker-Netzwerk (z.B. `["172.16.0.0/12"]`)
2. **Kong Route:** Ändere die Kong-Route für den Service `openclaw-admin` via Admin-API (Port 32777):
   - Setze `strip_path: false`.
3. **Restart:** Starte den OpenClaw Container neu.

## 3. WORST-CASE PRIMAT (Ersatzpfade)
- **Fehlschlag der basePath-Konfiguration:** Sollte OpenClaw den Parameter ignorieren, versuche die Umgebungsvariable `BASE_PATH=/openclaw` in der `.env` zu setzen.
- **Fehlschlag Kong-Routing:** Sollte `strip_path: false` zu 404-Fehlern führen (weil OpenClaw das `/openclaw` Präfix intern nicht verarbeitet), stelle `strip_path` zurück auf `true` und versuche eine alternative Kong-Route für `/assets` anzulegen, die global auf OpenClaw zeigt (nicht empfohlen, aber Ersatzpfad).
- **Rollback:** Wenn gar nichts mehr geht, stelle den Ursprungszustand (`strip_path: true`, keine Config-Änderung) wieder her.

## 4. ABWEICHUNGS-MELDEPFLICHT
Sollte die Konfigurationsdatei ein anderes Schema haben oder die Parameter in der aktuellen v4.16 anders heißen, melde dies detailliert.

## 5. VETO-TRAP (Beweis)
Beweise via `curl -s http://localhost:32776/openclaw | grep "/openclaw/assets"`, dass die Applikation nun die korrekten, präfixierten Asset-Pfade ausliefert. Melde erst dann Vollzug.

## 6. POST-FLIGHT WRITE
Integiere die Lösung atomar in `OPENCLAW_HOSTINGER_SPEZIFIKATIONEN.md` im Wiki. Keine Tagebücher!