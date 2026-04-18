<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# OpenClaw Hostinger Spezifikationen

Dieses Dokument definiert die spezifischen Konfigurationen für OpenClaw auf dem Hostinger-VPS.

## 1. Konfigurationspfade

| Typ | Pfad auf dem Host | Pfad im Container |
|---|---|---|
| **Ist-Zustand (Runtime)** | `/opt/openclaw/data/openclaw.json` | `/home/node/.openclaw/openclaw.json` |
| **Deploy-Skript (Soll)** | `/opt/omega-core/openclaw-admin/data/openclaw.json` | `/home/node/.openclaw/openclaw.json` |

> **Hinweis:** Es besteht aktuell eine Diskrepanz zwischen dem Pfad im `deploy_vps_full_stack.py` Skript und dem tatsächlich laufenden Container `openclaw-openclaw-gateway-1`. Änderungen müssen primär am Runtime-Pfad vorgenommen werden.

## 2. CORS & Origin Security (Control UI)

Um den Zugriff auf die Control UI über Proxies (z.B. Kong auf Port 32776) oder externe IPs zu ermöglichen, muss der `gateway.controlUi` Block wie folgt konfiguriert sein:

```json
"controlUi": {
  "enabled": true,
  "allowedOrigins": [
    "*",
    "http://localhost:18789",
    "http://127.0.0.1:18789",
    "https://187.77.68.250",
    "https://127.0.0.1",
    "http://187.77.68.250:32776"
  ],
  "dangerouslyAllowHostHeaderOriginFallback": true,
  "allowInsecureAuth": true,
  "dangerouslyDisableDeviceAuth": true,
  "basePath": "/openclaw"
}
```

### Parameter-Erklärung:
- **allowedOrigins**: Liste der erlaubten Ursprünge. `http://187.77.68.250:32776` ist zwingend für den Zugriff via Kong notwendig.
- **allowInsecureAuth**: Erlaubt Authentifizierung über ungesicherte Verbindungen (HTTP). Notwendig, wenn kein SSL am Gateway direkt anliegt.
- **dangerouslyDisableDeviceAuth**: Deaktiviert die Prüfung der Device-Identity, die normalerweise HTTPS oder einen Secure Context erfordert.

## 3. Neustart

Nach jeder Änderung an der `openclaw.json` muss der Container neu gestartet werden:
`docker restart openclaw-openclaw-gateway-1`

## 4. Bootstrap Prozess ("Bootstrap pending" auflösen)

Wenn das OpenClaw UI den Fehler `[Bootstrap pending] Please read BOOTSTRAP.md from the workspace and follow it before replying normally.` anzeigt, befindet sich die Instanz im uninitialisierten Zustand. 

Zur Behebung:
1. Prüfe das Workspace-Verzeichnis auf dem VPS (i.d.R. unter `/opt/openclaw/workspace/`).
2. Optional: Fülle `IDENTITY.md`, `USER.md` und `SOUL.md` mit den OMEGA CORE Spezifikationen, falls diese noch leer sind.
3. Lösche zwingend die Datei `BOOTSTRAP.md` im Workspace.
4. Starte den Container neu (`docker restart openclaw-openclaw-gateway-1`), damit der Gateway-Status aktualisiert wird.

## 5. Modell-Eichung (Gemini 3.1 Pro)

Um das Primärmodell festzulegen, muss die Datei `/opt/openclaw/data/openclaw.json` angepasst werden.
Der `agents.defaults.model.primary` Wert muss auf `google/gemini-3.1-pro-preview` gesetzt werden:

```json
  "agents": {
    "defaults": {
      "model": {
        "primary": "google/gemini-3.1-pro-preview",
        "fallbacks": [
          "google/gemini-2.5-pro"
        ]
      }
    }
  }
```
OpenClaw unterstützt Hot-Reloading für diese config. Die Logs zeigen: `config change detected; evaluating reload (agents.defaults.model.primary, agents.defaults.model.fallbacks)`.

## 6. Bekannte Bugs und Limitationen (Forschung 2026)

### 6.1 OpenClaw Core Bugs
- **Infinite Retry Loops auf Tool-Fehler:** Fehlen Parameter (z.B. `read({})` ohne Pfad), versucht das Modell dies endlos zu wiederholen, da es kein Signal erhält, dass der Fehler nicht retryable ist. Folge: Context Window Exhaustion.
- **Context Overflow durch Tool Results:** Es gibt keine Preflight-Guards für große Resultate (z.B. 560k+ Zeichen JSON). Führt sofort zu "prompt is too long" Fehlern und Stuck-Failure-Loops.
- **Infinite Session Context Accumulation:** Session-Historie wächst unbegrenzt (`sessions.json`). Dies führt irgendwann zu permanenten HTTP 400 Fehlern. Workaround: `sessions.json` manuell löschen und Gateway neustarten.
- **API Cooldown Block:** Ein einzelner Anthropic Timeout löst einen harten 30-60 Minuten Cooldown aus. Dies blockiert fälschlicherweise alle Fallbacks (auch OpenRouter).
- **UI Freezing:** Die Webchat-UI friert bei Sessions >500 Nachrichten ein (fehlende Pagination/Virtualization).

### 6.2 Hostinger VPS / MCP Spezifika
- **MCP Bulk Failures:** Auf VPS Instanzen (z.B. 5 CPU / 6GB RAM) schlägt die Initialisierung mehrerer MCP Server gleichzeitig manchmal fehl (Timing-/Buffering-Limits). **Workaround:** "Dummy" MCPs hinzufügen, die absichtlich zuerst fehlschlagen, um Pufferzeit für die eigentlichen MCPs in der nachfolgenden Batch-Reihenfolge zu schaffen.


## 7. Tool-Spezifikation & Installation (OC Brain & OC Spine)

Um OpenClaw mit den Fähigkeiten für das OMEGA Framework auszustatten, wurden gezielt Plugins, Skills und MCP-Server installiert und mit den internen Docker-Netzwerken (`evolution-api-yxa5_default`, `atlas_net`) verknüpft.

### 7.1 OC Brain (Kommunikation & Triage)
Für die Kommunikation nach außen (Evolution API, WhatsApp) und intelligentes Model-Routing:
- **WhatsApp & Webhooks Plugins:** `openclaw plugins enable whatsapp` und `webhooks` (für Evolution API Inbound/Outbound).
- **Model Router Skill:** `openclaw skills install openclaw-model-router-skill` (Für die Triage-Routings und Kostenkontrolle zwischen Haiku und Opus).
- **Triage Skill:** `openclaw skills install openclaw-triage` (Für Incident Response).

### 7.2 OC Spine (Persistenz & Archiv)
Für den Zugriff auf die produktive Datenbank und das Wiki wurden MCP-Server registriert und das Gateway mit den entsprechenden Netzwerken verbunden (`docker network connect evolution-api-yxa5_default openclaw-openclaw-gateway-1`):
- **PostgreSQL (Evolution API):** `openclaw mcp set postgres '{"command":"npx","args":["-y","@modelcontextprotocol/server-postgres","postgresql://evolution:uhLkGfm20w8nAxJSmJy9owxog8JoHiDg@evolution-api-yxa5-postgres-1:5432/evolution"]}'`
- **Filesystem / Wiki:** Da der `mcp-server` auf dem Host über TCP (Port 8001) via `socat` bereitgestellt wird, wurde ein Node.js TCP-Proxy (`/home/node/.openclaw/tcp-mcp.js`) im OpenClaw-Container implementiert, um den TCP-Stream in Standard-I/O (stdio) umzuwandeln.
  `openclaw mcp set filesystem '{"command":"node","args":["/home/node/.openclaw/tcp-mcp.js","mcp-server","8001"]}'`
- **ChromaDB API:** REST-Zugriff über `mcp-fetch` oder das Webhooks Plugin (Ersatz für einen nativen ChromaDB-MCP).

*Hinweis: Nach diesen Änderungen lädt OpenClaw die Konfiguration in der Regel via Hot-Reload, alternativ den Container neu starten.*
