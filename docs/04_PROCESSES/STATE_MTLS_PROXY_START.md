# State mTLS-Proxy (localhost:8049)

**Zweck:** Lokaler HTTP-Endpunkt für `mcp_omega_state` (`read_handbook`, `update_handbook`, `/state`) → HTTPS+mTLS zum VPS (`VPS_HOST`, Pfad unter `/core_api/…`).

**Nicht** Teil des **InfrastructureSentinel** / VPS-Heartbeats: `127.0.0.1` ist nur auf dem Rechner erreichbar, auf dem Cursor den MCP startet.

## Start

```bash
cd /OMEGA_CORE
PYTHONPATH=/OMEGA_CORE .venv/bin/python -m src.daemons.state_mtls_proxy
```

Standard: lauscht auf **127.0.0.1:8049** (im Modul `__main__` fest).

## Zertifikate (Client mTLS)

| Variable | Bedeutung |
|----------|-----------|
| `STATE_PROXY_CERT_PEM` | Client-Zertifikat (PEM) |
| `STATE_PROXY_CERT_KEY` | Private Key |
| `STATE_PROXY_CA` | CA/Chain für Server-Verify (optional; fehlt Datei → `verify=False` im Upstream-Client) |

**Defaults:** `data/certs/mtho-client.pem`, `mtho-client.key`, `chain_server.pem`.
Wenn **mtho**-Dateien fehlen und **`data/certs/cursor.pem`** + **`cursor.key`** existieren → diese als Fallback.

Ohne nutzbare Zertifikatdateien startet der Proxy **nicht** (klarer Log, Exit **1**).

## MCP ohne Proxy

`read_handbook` / `update_handbook` fallen bei fehlendem **8049** auf Dateien unter `docs/03_INFRASTRUCTURE/handbooks/{role}.md` zurück (lokal, kein VPS).
