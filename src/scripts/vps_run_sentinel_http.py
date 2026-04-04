# -*- coding: utf-8 -*-
"""
VPS: Minimaler HTTP-Ingress für den Sentinel (Ticket 12).

POST /ingest  JSON: {"source": "ha", "payload": {...}, "V": 0.9, "R": 0.05}
Body-Felder V/R optional (Pacemaker); fehlen sie, wird /etc/omega/pacemaker.json gelesen.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("vps_run_sentinel_http")

_PACEMAKER_PATH = Path(
    os.environ.get("OMEGA_PACEMAKER_STATE_PATH", "/etc/omega/pacemaker.json")
)
_BIND = os.environ.get("OMEGA_SENTINEL_BIND", "127.0.0.1")
_PORT = int(os.environ.get("OMEGA_SENTINEL_PORT", "18080"))


def _load_pacemaker_file() -> dict[str, Any]:
    try:
        raw = _PACEMAKER_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _merge_pacemaker(body: dict[str, Any]) -> dict[str, Any]:
    base = _load_pacemaker_file()
    out = {**base}
    if "V" in body:
        out["V"] = body["V"]
    if "R" in body:
        out["R"] = body["R"]
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        log.info("%s - %s", self.address_string(), fmt % args)

    def do_GET(self) -> None:
        if self.path in ("/", "/health"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/ingest":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
        if not isinstance(body, dict):
            self.send_response(400)
            self.end_headers()
            return

        source = (body.get("source") or "").strip()
        payload = body.get("payload")
        if not source or not isinstance(payload, dict):
            self.send_response(400)
            self.end_headers()
            return

        pacemaker = _merge_pacemaker(body)

        async def _go() -> None:
            from src.daemons import vps_sentinel_daemon as sentinel

            await sentinel.process_inbound_event(source, payload, pacemaker)

        try:
            asyncio.run(_go())
        except Exception:
            log.exception("ingest_failed source=%s", source)
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{\"accepted\":true}\n")


def main() -> None:
    srv = ThreadingHTTPServer((_BIND, _PORT), Handler)
    log.info("sentinel_http listening %s:%s", _BIND, _PORT)
    srv.serve_forever()


if __name__ == "__main__":
    repo = os.environ.get("OMEGA_REPO_ROOT", "/opt/omega")
    if repo not in sys.path:
        sys.path.insert(0, repo)
    main()
