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
