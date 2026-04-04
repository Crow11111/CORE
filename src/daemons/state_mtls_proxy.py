# -*- coding: utf-8 -*-
"""
OMEGA STATE mTLS Proxy (Lokal -> VPS)
VECTOR: 2210 | DELTA: 0.049

Ermöglicht lokalen Sub-Agenten auf Dreadnought via `http://localhost:8049`
mit dem sicheren VPS-Endpunkt zu kommunizieren, ohne SSL-Zertifikate laden zu müssen.
"""
from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250")
VPS_BASE_URL = f"https://{VPS_HOST}/core_api"

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
_CERT_DIR = os.path.join(_REPO_ROOT, "data", "certs")

# Gesetzt in lifespan nach erfolgreicher Validierung
_CLIENT_CERT_PEM: str = ""
_CLIENT_CERT_KEY: str = ""
_HTTPS_VERIFY: str | bool = False


def _resolve_state_proxy_cert_paths() -> tuple[str, str, str]:
    """(cert_pem, cert_key, ca_path) — ca_path ist Default-Pfad auch wenn Datei fehlt."""
    pem_e = os.getenv("STATE_PROXY_CERT_PEM")
    key_e = os.getenv("STATE_PROXY_CERT_KEY")
    ca_e = os.getenv("STATE_PROXY_CA")

    mtho_pem = os.path.join(_CERT_DIR, "mtho-client.pem")
    mtho_key = os.path.join(_CERT_DIR, "mtho-client.key")
    cur_pem = os.path.join(_CERT_DIR, "cursor.pem")
    cur_key = os.path.join(_CERT_DIR, "cursor.key")
    default_ca = os.path.join(_CERT_DIR, "chain_server.pem")

    if pem_e:
        pem = pem_e
    elif os.path.isfile(mtho_pem):
        pem = mtho_pem
    elif os.path.isfile(cur_pem):
        pem = cur_pem
    else:
        pem = mtho_pem

    if key_e:
        key = key_e
    elif os.path.isfile(mtho_key):
        key = mtho_key
    elif os.path.isfile(cur_key):
        key = cur_key
    else:
        key = mtho_key

    ca = ca_e if ca_e else default_ca
    return pem, key, ca


def _validate_client_tls_or_exit(pem: str, key: str) -> None:
    missing: list[str] = []
    if not os.path.isfile(pem):
        missing.append(f"Client-Zertifikat fehlt: {pem}")
    if not os.path.isfile(key):
        missing.append(f"Client-Key fehlt: {key}")
    if missing:
        print(
            "[FEHLER] state_mtls_proxy: Kein nutzbares mTLS-Client-Zertifikat — Abbruch.",
            file=sys.stderr,
        )
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print(
            "  Setze STATE_PROXY_CERT_PEM / STATE_PROXY_CERT_KEY oder lege "
            "mtho-client.pem+.key oder cursor.pem+.key unter data/certs ab.",
            file=sys.stderr,
        )
        sys.exit(1)


def _https_verify_arg(ca_path: str) -> str | bool:
    if os.path.isfile(ca_path):
        return ca_path
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _CLIENT_CERT_PEM, _CLIENT_CERT_KEY, _HTTPS_VERIFY
    pem, key, ca = _resolve_state_proxy_cert_paths()
    _validate_client_tls_or_exit(pem, key)
    _CLIENT_CERT_PEM = pem
    _CLIENT_CERT_KEY = key
    _HTTPS_VERIFY = _https_verify_arg(ca)
    print(f"[*] mTLS Proxy -> {VPS_BASE_URL}")
    print(f"[*] Client Cert: {pem}")
    print(f"[*] Client Key:  {key}")
    print(f"[*] HTTPS verify: {_HTTPS_VERIFY!r}")
    yield


app = FastAPI(
    title="OMEGA State mTLS Proxy",
    version="1.0.0",
    lifespan=lifespan,
)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """
    Fängt alle Anfragen ab und leitet sie 1:1 via HTTPS+mTLS an den VPS weiter.
    """
    url = f"{VPS_BASE_URL}/{path}"

    params = dict(request.query_params)
    body = await request.body()

    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(
        verify=_HTTPS_VERIFY,
        cert=(_CLIENT_CERT_PEM, _CLIENT_CERT_KEY),
        timeout=10.0,
    ) as client:
        try:
            proxy_req = client.build_request(
                method=request.method,
                url=url,
                params=params,
                headers=headers,
                content=body,
            )
            proxy_resp = await client.send(proxy_req)

            resp_headers = dict(proxy_resp.headers)
            resp_headers.pop("content-encoding", None)
            resp_headers.pop("content-length", None)

            return Response(
                content=proxy_resp.content,
                status_code=proxy_resp.status_code,
                headers=resp_headers,
            )
        except httpx.RequestError as exc:
            print(f"[FAIL] Routing Fehler: {exc}")
            return JSONResponse(
                status_code=502,
                content={"error": "Bad Gateway", "details": str(exc)},
            )


def _preflight_cli_or_exit() -> None:
    """Synchroner Check vor uvicorn.run (__main__)."""
    pem, key, ca = _resolve_state_proxy_cert_paths()
    _validate_client_tls_or_exit(pem, key)
    v = _https_verify_arg(ca)
    print(f"[*] Preflight OK -> {VPS_BASE_URL} | cert={pem} | verify={v!r}")


if __name__ == "__main__":
    _preflight_cli_or_exit()
    uvicorn.run(app, host="127.0.0.1", port=8049, reload=False)
