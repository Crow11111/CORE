# MASTERPLAN: KONG ROUTING FÜR OPENCLAW & EVOLUTION API (THE WIRING)

**Vektor:** 2210 | **Delta:** 0.049 | **Status:** PENDING O2 AUDIT (REVISION 1)

## 1. ZIEL
Der API-Gateway Bypass (Evolution feuert Webhooks auf öffentliche IP direkt an OpenClaw) muss geschlossen werden. 
Das Routing muss den internen VPS-Verkehr auf das Kong-Gateway (Host-Port 32776) bündeln.

## 2. TEAMBILDUNG & PROFIL (Der 3-Instanzen-Workflow)
- **Rolle:** OMEGA Network Surgeon (Team-Lead)
- **Wissen & Skills:** Kong Admin API (`/services`, `/routes`), Evolution API, Docker Networking.
- **Werkzeuge:** `curl`, `jq`, `ssh`, `.env` Variablen.
- **Framing:** Du bist misstrauisch. Du glaubst nicht an `172.17.0.1`, bis ein `curl` beweist, dass es erreichbar ist. Du erstellst Services nur, wenn sie davor nicht existieren, oder patchst sie. Du nutzt keine öffentlichen IPs.
- **Kontext:** `~/OMEGA_WIKI/wiki/NETZWERK_PORTS.md`, `~/OMEGA_WIKI/wiki/HOSTINGER_VPS_SPEZIFIKA.md`, `.env`.

## 3. SEQUENZIELLER ABLAUF & BEWEISLAST (Worst-Case-Primat)
1. **Schritt 1 (Beweis):** Der Surgeon prüft per SSH auf dem VPS, ob `172.17.0.1:18789` (OpenClaw) und `172.17.0.1:32776` (Kong) vom Host aus erreichbar sind. 
   - *Ersatzpfad:* Sollte `172.17.0.1` nicht auflösen, sucht er die echte Host-IP via `ip a` oder das `docker0` Interface.
2. **Schritt 2 (Kong Wiring):** Der Surgeon konfiguriert via `curl http://localhost:32777` die Kong Admin API:
   - Erzeugt den Service `openclaw-admin` mit der bewiesenen Host-URL (`http://172.17.0.1:18789`).
   - Erzeugt die Route `/openclaw` (mit `strip_path=true`) für den Service.
3. **Schritt 3 (Evolution Wiring):** Der Surgeon ändert die Webhook-URL in der Evolution API (Port 55775) auf `http://172.17.0.1:32776/openclaw/webhook/whatsapp`. (Die API verlangt den `EVOLUTION_API_KEY` Header).
4. **Schritt 4 (Telemetrie):** 
   - Surgeon ruft `curl -s http://localhost:32777/routes | jq '.data[] | select(.name=="openclaw-route")'` auf.
   - Surgeon ruft `curl -s http://localhost:55775/webhook/find/Marc%20ten%20Hoevel -H 'apikey: <KEY>'` auf.

## 4. VETO-TRAPS (Für O2 zur finalen Freigabe)
- **Veto**, wenn der Surgeon die Admin-URL oder Webhook-URL auf öffentliche externe IPs routet.
- **Veto**, wenn die Telemetrie am Ende keine erfolgreiche Kong-Route oder eine unveränderte Webhook-URL liefert.
- **Veto**, wenn der Surgeon nicht vorab die IP empirisch testet.