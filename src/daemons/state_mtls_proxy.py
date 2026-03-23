# -*- coding: utf-8 -*-
"""
OMEGA STATE mTLS Proxy (Lokal -> VPS)
VECTOR: 2210 | DELTA: 0.049

Ermöglicht lokalen Sub-Agenten auf Dreadnought via `http://localhost:8049`
mit dem sicheren VPS-Endpunkt zu kommunizieren, ohne SSL-Zertifikate laden zu müssen.
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="OMEGA State mTLS Proxy", version="1.0.0")

# Konfiguration
VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250")
VPS_BASE_URL = f"https://{VPS_HOST}/core_api"

CERT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "certs")
CERT_PEM = os.path.join(CERT_DIR, "mtho-client.pem")
CERT_KEY = os.path.join(CERT_DIR, "mtho-client.key")
CA_ROOT = os.path.join(CERT_DIR, "chain_server.pem")  # Behebt certificate verify failed

@app.on_event("startup")
async def startup_event():
    print(f"[*] Starting mTLS Proxy -> {VPS_BASE_URL}")
    print(f"[*] Using Client Cert: {CERT_PEM}")
    print(f"[*] Using Client Key:  {CERT_KEY}")
    print(f"[*] Using CA Root:     {CA_ROOT}")
    
    # Validiere dass Dateien existieren
    for f in [CERT_PEM, CERT_KEY, CA_ROOT]:
        if not os.path.exists(f):
            print(f"[FEHLER] Zertifikat nicht gefunden: {f}")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """
    Fängt alle Anfragen ab und leitet sie 1:1 via HTTPS+mTLS an den VPS weiter.
    """
    url = f"{VPS_BASE_URL}/{path}"
    
    # Extrahiere Query Params und Body
    params = dict(request.query_params)
    body = await request.body()
    
    headers = dict(request.headers)
    # Host-Header überschreiben / entfernen um Probleme mit dem Zielserver zu vermeiden
    headers.pop("host", None)
    
    async with httpx.AsyncClient(
        verify=False,
        cert=(CERT_PEM, CERT_KEY),
        timeout=10.0
    ) as client:
        try:
            proxy_req = client.build_request(
                method=request.method,
                url=url,
                params=params,
                headers=headers,
                content=body
            )
            proxy_resp = await client.send(proxy_req)
            
            # WICHTIG: Erlaubt Rückgabe an Agenten
            resp_headers = dict(proxy_resp.headers)
            resp_headers.pop("content-encoding", None)
            resp_headers.pop("content-length", None)
            
            return Response(
                content=proxy_resp.content,
                status_code=proxy_resp.status_code,
                headers=resp_headers
            )
        except httpx.RequestError as exc:
            print(f"[FAIL] Routing Fehler: {exc}")
            return JSONResponse(
                status_code=502,
                content={"error": "Bad Gateway", "details": str(exc)}
            )

if __name__ == "__main__":
    uvicorn.run("state_mtls_proxy:app", host="127.0.0.1", port=8049, reload=False)
