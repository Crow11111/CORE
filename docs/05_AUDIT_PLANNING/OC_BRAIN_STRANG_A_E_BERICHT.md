# OC Brain – Strang A (Diagnose) & Strang E (WhatsApp) – Kurzbericht

**Erstellt:** Security Expert (Strang A, E)  
**Bezug:** [OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md](OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md), [OPENCLAW_GATEWAY_TOKEN.md](../02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md), [WHATSAPP_ROUTING_CORE_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_CORE_OC.md)

---

## 1. Strang A: OpenClaw Doctor (A2)

### Ausführung

- **Befehl:** `python -m src.scripts.openclaw_doctor_vps` (Projektroot, `PYTHONIOENCODING=utf-8`).
- **SSH:** Nutzung von `.env` – `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` (bzw. Passwort). Keine Credentials in diesem Bericht.
- **Container-Ermittlung:** `docker ps --format '{{.Names}}' | grep -iE 'openclaw|hvps' | head -1`
- **Getroffener Container:** `openclaw-spine`

### A2-Status: **NICHT OK** (Doctor mit Fehlern / Exit 137)

**Exit-Code:** 137 (Container/Prozess beendet, typisch OOM oder Signal).

**Doctor-Ausgabe (Zusammenfassung):**

| Bereich        | Befund |
|----------------|--------|
| **State-Integrität** | State-Verzeichnis zu offen (`~/.openclaw`). Empfehlung: `chmod 700`. Config-Datei gruppen-/weltlesbar (`~/.openclaw/openclaw.json`). Empfehlung: `chmod 600`. |
| **OAuth/Pairing** | OAuth-Verzeichnis fehlt (`~/.openclaw/credentials`). Hinweis: „Skipping create because **no WhatsApp/pairing channel config is active**“. |
| **Sessions** | 1/1 aktuelle Sessions ohne Transkripte. Pfad: `~/.openclaw/agents/main/sessions/sessions.json`. Main-Session-Transkript fehlt (eine .jsonl-Datei). „History will appear to reset.“ |
| **Security** | Gateway an „lan“ (0.0.0.0) gebunden – netzwerkweit erreichbar. Empfehlung: Auth stark halten; alternativ Loopback + Tailscale/SSH-Tunnel. |
| **Skills** | Eligible: 3, Missing requirements: 48, Blocked by allowlist: 0. |

**Relevante Config-Pfade (im Container):**

- Config: `~/.openclaw/openclaw.json` (auf Host je nach Setup z. B. `./openclaw-spine/data/openclaw.json` oder bei Full-Stack Admin: `/opt/core-core/openclaw-admin/data/openclaw.json`).
- Sessions: `~/.openclaw/agents/main/sessions/sessions.json`.

**Hinweis:** Das Skript wählt den **ersten** laufenden OpenClaw-Container (`openclaw-spine`). Für A2 im Sinne der Admin-Instanz (WhatsApp, Channels) sollte `openclaw doctor` ggf. explizit im Container **openclaw-admin** ausgeführt werden:

```bash
docker exec openclaw-admin openclaw doctor
```

---

## 2. Strang E: WhatsApp in OC Admin

### Wo wird der WhatsApp-Channel aktiviert?

- **Im OpenClaw Admin (Dashboard):** Laut [OPENCLAW_ZWISCHENZIELE.md](OPENCLAW_ZWISCHENZIELE.md) (Z3/Z4): unter **Agents / Channels / Config / Chat** – dort ist der **WhatsApp-Channel** sichtbar und konfigurierbar („WhatsApp-Channel sichtbar, Config editierbar“).
- **In der Config-Datei:** In `openclaw.json` muss der Channel `whatsapp` unter `channels.whatsapp` aktiv sein (inkl. z. B. `dmPolicy`, `allowFrom`, `textChunkLimit`). Referenz: [WHATSAPP_OPENCLAW_BRIDGE.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_BRIDGE.md), [WHATSAPP_OPENCLAW_VS_HA.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md). Deploy-Skripte setzen `channels.whatsapp` in der Admin-Config (z. B. `deploy_vps_full_stack.py`, `deploy_openclaw_config_vps.py`).

### Wie wird der QR-Code für Pairing generiert?

- **CLI (VPS/Container):** Im Admin-Container auf dem VPS:
  - `docker exec openclaw-admin openclaw channels login whatsapp`
  - Der QR-Code erscheint in der Konsole (ASCII/Terminal). Mit dem dedizierten Smartphone unter WhatsApp → „Verbundene Geräte“ scannen.
- **Admin-UI:** Doku erwähnt „bzw. via Admin-UI“ ([WHATSAPP_OPENCLAW_BRIDGE.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_BRIDGE.md)); konkrete URL/Button für QR in der UI sind dort nicht festgehalten – aktuell sichere Methode: obiger CLI-Befehl im Container.

**Schritte für QR-Pairing (Strang E):**

1. SSH auf VPS (User/Host aus `.env`).
2. Sicherstellen, dass der **openclaw-admin**-Container läuft und in seiner Config `channels.whatsapp` aktiv ist (z. B. in `/opt/core-core/openclaw-admin/data/openclaw.json`).
3. Im Admin-Container ausführen: `docker exec openclaw-admin openclaw channels login whatsapp`.
4. QR-Code im Terminal anzeigen lassen (ggf. Terminal-Fenster groß genug / Zeichensatz UTF-8).
5. Auf dem Smartphone: WhatsApp → Einstellungen → Verbundene Geräte → Gerät verbinden → QR-Code scannen.
6. Nach erfolgreichem Pairing: Testnachricht an die verknüpfte Nummer senden (z. B. „@OC Ping“); Antwort prüfen. Routing: [WHATSAPP_ROUTING_CORE_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_CORE_OC.md).

### Config-Status (WhatsApp-Channel „whatsapp“)

- **openclaw-spine (von Doctor geprüft):** Doctor meldet: **kein aktiver WhatsApp/Pairing-Channel** („no WhatsApp/pairing channel config is active“). Dort ist der WhatsApp-Kanal also nicht aktiv – konsistent mit der Rolle der Spine-Instanz (keine Messenger-Keys).
- **openclaw-admin:** Nicht per Doctor geprüft. Die Aktivierung von `channels.whatsapp` erfolgt durch die Deploy-Skripte (`deploy_vps_full_stack.py` / `deploy_openclaw_config_vps.py`) für die Admin-Config unter `/opt/core-core/openclaw-admin/data/openclaw.json`. Ob die Datei auf dem VPS aktuell `channels.whatsapp` enthält, muss vor dem Pairing auf dem Server geprüft werden (z. B. `grep -A5 '"channels"' /opt/core-core/openclaw-admin/data/openclaw.json` oder Datei einsehen – ohne Tokens/Secrets im Bericht).

---

## 3. Manuell noch zu tun

| Aktion | Beschreibung |
|--------|--------------|
| **A2 abschließen** | Doctor im Container **openclaw-admin** ausführen; State-Berechtigungen (chmod 700/600) und Session-Transkripte beheben; Exit 137 prüfen (Ressourcen/Logs). Ziel: `openclaw doctor` ohne Fehler (Exit 0). |
| **QR scannen** | `docker exec openclaw-admin openclaw channels login whatsapp` auf dem VPS ausführen, QR mit Handy scannen (WhatsApp → Verbundene Geräte). |
| **Testnachricht** | Nach Pairing eine Nachricht an die verknüpfte Nummer senden (z. B. „@OC Ping“), Antwort und Logs prüfen. |
| **Routing** | Sicherstellen, dass @Core vs. @OC wie in [WHATSAPP_ROUTING_CORE_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_CORE_OC.md) umgesetzt ist. |

---

## 4. Referenzen

- Strang A/E Auftrag: [OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md](OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md)
- Gateway-Token: [OPENCLAW_GATEWAY_TOKEN.md](../02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md)
- WhatsApp-Routing: [WHATSAPP_ROUTING_CORE_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_CORE_OC.md)
- WhatsApp/OC-Bridge: [WHATSAPP_OPENCLAW_BRIDGE.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_BRIDGE.md), [WHATSAPP_OPENCLAW_VS_HA.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md)
- Zwischenziele/UI: [OPENCLAW_ZWISCHENZIELE.md](OPENCLAW_ZWISCHENZIELE.md)
- Doctor-Skript: `src/scripts/openclaw_doctor_vps.py`
