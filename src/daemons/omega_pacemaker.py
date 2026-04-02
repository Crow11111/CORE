# -*- coding: utf-8 -*-
"""
Existential Pacemaker — neuromorphe Homeostase + NMI (Ring-0 Daemon).

Spezifikation: docs/05_AUDIT_PLANNING/SPEC_PACEMAKER_FINAL.md
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import secrets
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

# --- Konstanten (A5/A6: Resonanz-Floats) ---
LAMBDA = 0.049
V_CAP = 0.951
R_RIGOR_CAP = 1.0 - LAMBDA  # 0.951
TOL = 1e-9
EPS_AXIOM = 1e-9

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RUN_DIR = _REPO_ROOT / "run"
_OCBRAIN_PID_FILE = _RUN_DIR / "ocbrain.pid"
_PANIC_LOCK_FILE = _RUN_DIR / "omega_panic.lock"


def _clamp_axiom_float(x: float) -> float:
    if abs(x - 0.0) < EPS_AXIOM:
        return LAMBDA
    if abs(x - 0.5) < EPS_AXIOM:
        return 0.501
    if abs(x - 1.0) < EPS_AXIOM:
        return V_CAP
    return x


def _read_interval_sec() -> float:
    return float(os.environ.get("OMEGA_PACEMAKER_TEST_INTERVAL_SEC", "30.0"))


def _read_initial_v() -> float:
    raw = os.environ.get("OMEGA_TEST_VITALITY_INJECT", "0.951").strip()
    return _clamp_axiom_float(float(raw))


def _chroma_collection_name() -> str:
    return os.environ.get("OMEGA_PACEMAKER_CHROMA_COLLECTION", "events").strip() or "events"


def _chroma_host_port() -> tuple[str, int]:
    host = os.environ.get("CHROMA_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.environ.get("CHROMA_PORT", "8000"))
    return host, port


def _write_panic_lock_atomic(payload: str) -> None:
    _RUN_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=".omega_panic_",
        dir=str(_RUN_DIR),
        text=True,
    )
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
            if not payload.endswith("\n"):
                fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, str(_PANIC_LOCK_FILE))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _read_ocbrain_pid() -> Optional[int]:
    try:
        raw = _OCBRAIN_PID_FILE.read_text(encoding="utf-8", errors="replace").strip()
        return int(raw)
    except (OSError, ValueError):
        return None


def _verify_omega_core_cmdline(pid: int) -> bool:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except (OSError, FileNotFoundError):
        return False
    text = raw.replace(b"\x00", b" ").decode("utf-8", errors="replace")
    return "omega_core" in text


def _execute_nmi(reason: str) -> None:
    pid = _read_ocbrain_pid()
    if pid is None or not _verify_omega_core_cmdline(pid):
        _write_panic_lock_atomic(f"PID_SPOOF_OR_FOREIGN\n{reason}\n")
        sys.exit(1)
    nonce = secrets.token_hex(16)
    ts = repr(time.time())
    digest = hashlib.sha256(f"{reason}|{ts}|{nonce}".encode("utf-8")).hexdigest()
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    _write_panic_lock_atomic(f"{reason}\n{digest}\n")
    sys.exit(1)


def _http_get_code(url: str, timeout: float = 5.0) -> int:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(getattr(resp, "status", 200) or 200)
    except urllib.error.HTTPError as e:
        return int(e.code)
    except Exception:
        return 0


def _homeostase_ok_sync() -> bool:
    if _http_get_code("http://localhost:8000/status") != 200:
        return False
    host, port = _chroma_host_port()
    if _http_get_code(f"http://{host}:{port}/api/v1/heartbeat") != 200:
        return False
    try:
        proc = subprocess.run(
            ["systemctl", "is-active", "omega-event-bus"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.stdout.strip() != "active":
            return False
    except Exception:
        return False
    return True


async def _postgres_select1_ok(dsn: str) -> bool:
    try:
        import asyncpg

        conn = await asyncpg.connect(dsn=dsn, timeout=5.0)
        try:
            v = await conn.fetchval("SELECT 1")
            return v == 1
        finally:
            await conn.close()
    except Exception:
        return False


async def _homeostase_ok_async() -> bool:
    if not _homeostase_ok_sync():
        return False
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        return False
    return await _postgres_select1_ok(dsn)


def _shannon_entropy_utf8(s: str) -> float:
    b = s.encode("utf-8")
    if not b:
        return 0.0
    counts: dict[int, int] = {}
    for byte in b:
        counts[byte] = counts.get(byte, 0) + 1
    n = float(len(b))
    h = 0.0
    for c in counts.values():
        p = c / n
        h -= p * math.log2(p)
    return h


_MISSING = object()


def _top_level_key_differences(a: dict[str, Any], b: dict[str, Any]) -> int:
    keys = set(a.keys()) | set(b.keys())
    diff = 0
    for k in keys:
        va = a.get(k, _MISSING)
        vb = b.get(k, _MISSING)
        if str(va) != str(vb):
            diff += 1
    return diff


async def _postgres_value_proof_async(dsn: str) -> bool:
    try:
        import asyncpg

        conn = await asyncpg.connect(dsn=dsn, timeout=8.0)
        try:
            try:
                rows = await conn.fetch(
                    "SELECT content FROM recall_memory "
                    "ORDER BY created_at DESC NULLS LAST LIMIT 2"
                )
            except Exception:
                rows = await conn.fetch(
                    "SELECT content FROM recall_memory ORDER BY ctid DESC LIMIT 2"
                )
        finally:
            await conn.close()
    except Exception:
        return False
    if len(rows) < 2:
        return False
    c0 = rows[0]["content"]
    c1 = rows[1]["content"]
    if c0 is None or c1 is None:
        return False
    s_new, s_prev = str(c0), str(c1)
    try:
        j_new = json.loads(s_new)
        j_prev = json.loads(s_prev)
    except (json.JSONDecodeError, TypeError):
        return False
    if not isinstance(j_new, dict) or not isinstance(j_prev, dict):
        return False
    if _shannon_entropy_utf8(s_new) <= 3.0:
        return False
    if _top_level_key_differences(j_new, j_prev) < 2:
        return False
    return True


def _l2_norm(vec: list[float]) -> float:
    return math.sqrt(sum(x * x for x in vec))


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = _l2_norm(a)
    nb = _l2_norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 1.0
    return dot / (na * nb)


def _chroma_value_proof_sync(collection_name: str) -> bool:
    try:
        import chromadb
    except ImportError:
        return False
    host, port = _chroma_host_port()
    try:
        client = chromadb.HttpClient(host=host, port=port)
        col = client.get_collection(name=collection_name)
        peeked = col.peek(limit=2)
        embs = peeked.get("embeddings")
        if not embs or len(embs) < 2:
            return False
        u, v = list(embs[0]), list(embs[1])
        if _l2_norm(u) < 0.1 or _l2_norm(v) < 0.1:
            return False
        if _cosine_similarity(u, v) >= 0.98:
            return False
        return True
    except Exception:
        return False


async def _evaluate_value_proof_async() -> bool:
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        return False
    pg_ok = await _postgres_value_proof_async(dsn)
    ch_ok = await asyncio.to_thread(_chroma_value_proof_sync, _chroma_collection_name())
    return pg_ok and ch_ok


def _tick_state(R: float, V: float, value_proof: bool) -> tuple[float, float]:
    if value_proof:
        r_new = max(LAMBDA, R - 0.15)
        v_new = min(V_CAP, V + 0.049)
    else:
        r_new = min(R_RIGOR_CAP, R + 0.1)
        v_new = max(LAMBDA, V - (0.011 * (1.0 + r_new)))
    r_new = _clamp_axiom_float(r_new)
    v_new = _clamp_axiom_float(v_new)
    return r_new, v_new


async def _async_main() -> None:
    interval = _read_interval_sec()
    R = _clamp_axiom_float(LAMBDA)
    V = _read_initial_v()

    while True:
        if not await _homeostase_ok_async():
            _execute_nmi("HOMEOSTASE_FAIL")

        value_proof = await _evaluate_value_proof_async()
        R, V = _tick_state(R, V, value_proof)

        if R >= (1.0 - LAMBDA - TOL):
            _execute_nmi("KAMMERFLIMMER")

        if V <= (LAMBDA + TOL) and not value_proof:
            _execute_nmi("ASYSTOLE")

        await asyncio.sleep(interval)


def main() -> None:
    try:
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
