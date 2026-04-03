# -*- coding: utf-8 -*-
"""
Existential Pacemaker — VAR_3 neuromorphe Homeostase + NMI (Ring-0 Daemon).

Spezifikation: docs/05_AUDIT_PLANNING/SPEC_PACEMAKER_VAR_3.md
(Baseline NMI/Recovery: SPEC_PACEMAKER.md §2.2–2.3, AC-2/AC-4)
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import secrets
import signal
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path
from typing import Any, Optional

# --- Konstanten (A5/A6: Resonanz-Floats, VAR_3) ---
LAMBDA = 0.049
V_CAP = 0.951
R_RIGOR_CAP = 1.0 - LAMBDA
T_NOMINAL = 30.0
PHI = (1.0 + math.sqrt(5.0)) / 2.0
W_IBI = 17
M_MONO = 5
ETA_GAIN = 0.049
ETA_LOSS = 0.051
KAPPA_R = 0.237
EPS_FLOOR = 1e-12
SIGMA_LOW = 0.049
SIGMA_HIGH = 0.382
TOL = 1e-9
EPS_AXIOM = 1e-9
PATHOLOGY_R_THRESHOLD = 1.0 - LAMBDA - 1e-9
V_PATHOLOGY_CAP = V_CAP / PHI

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RUN_DIR = _REPO_ROOT / "run"
_OCBRAIN_PID_FILE = _RUN_DIR / "ocbrain.pid"
_PANIC_LOCK_FILE = _RUN_DIR / "omega_panic.lock"
_PATHOLOGY_LOG_FILE = _RUN_DIR / "omega_pacemaker_pathology.log"


def _clamp_axiom_float(x: float) -> float:
    if abs(x - 0.0) < EPS_AXIOM:
        return LAMBDA
    if abs(x - 0.5) < EPS_AXIOM:
        return 0.501
    if abs(x - 1.0) < EPS_AXIOM:
        return V_CAP
    return x


def _clamp_r(x: float) -> float:
    lo, hi = LAMBDA, R_RIGOR_CAP
    return max(lo, min(hi, x))


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


def _ibi_hrv_metrics(ibi: list[float]) -> tuple[float, float]:
    """RMSSD* und SDNN* aus IBI-Fenster; A5: nie exakt 0.0 speichern."""
    if len(ibi) < 2:
        base = _clamp_axiom_float(LAMBDA)
        return base, base
    diffs_sq = [(ibi[i] - ibi[i - 1]) ** 2 for i in range(1, len(ibi))]
    rmssd = math.sqrt(sum(diffs_sq) / len(diffs_sq))
    sdnn = statistics.pstdev(ibi)
    if rmssd <= 0.0 or math.isnan(rmssd):
        rmssd = LAMBDA
    else:
        rmssd = _clamp_axiom_float(rmssd)
    if sdnn <= 0.0 or math.isnan(sdnn):
        sdnn = LAMBDA
    else:
        sdnn = _clamp_axiom_float(sdnn)
    return rmssd, sdnn


def _compute_D(R: float, rmssd_star: float, T: float, phi: float) -> float:
    d = 0.0
    for s in (1, 2, 3):
        w_s = LAMBDA * (phi ** (s - 1))
        term = R - rmssd_star / (T * (phi**s))
        d += w_s * max(0.0, term)
    return d


def _update_v_exponential(V: float, R: float, D: float, value_proof: bool) -> float:
    """§4.3 — ausschließlich exp-Pfade auf (V−Λ)."""
    if value_proof:
        v_new = LAMBDA + (V - LAMBDA) * math.exp(-ETA_GAIN * (1.0 - R))
    else:
        v_new = LAMBDA + (V - LAMBDA) * math.exp(-ETA_LOSS * (1.0 + D) * (1.0 + R))
    if v_new <= LAMBDA:
        v_new = LAMBDA + EPS_FLOOR
    return _clamp_axiom_float(v_new)


def _monotonicity_boost_b_mono(mu_L_hist: deque[float]) -> float:
    if len(mu_L_hist) < M_MONO:
        return EPS_FLOOR
    recent = list(mu_L_hist)[-M_MONO:]
    if all(abs(recent[i] - recent[i - 1]) < LAMBDA for i in range(1, M_MONO)):
        return LAMBDA
    return EPS_FLOOR


def _update_r_from_metrics(
    R_prev: float,
    rmssd_star: float,
    T: float,
    mu_L_hist: deque[float],
) -> float:
    """§5.2 — σ_norm aus RMSSD* / T."""
    sigma_norm = rmssd_star / T if T > 0.0 else EPS_FLOOR
    if sigma_norm < SIGMA_LOW:
        S = (SIGMA_LOW - sigma_norm) / SIGMA_LOW
    elif sigma_norm <= SIGMA_HIGH:
        S = EPS_FLOOR
    else:
        S = min(1.0 - LAMBDA, (sigma_norm - SIGMA_HIGH) / (1.0 - SIGMA_HIGH))
    r_sigma = _clamp_r(LAMBDA + (1.0 - 2.0 * LAMBDA) * S)
    b_mono = _monotonicity_boost_b_mono(mu_L_hist)
    r_raw = _clamp_r(r_sigma + b_mono)
    R_new = R_prev + KAPPA_R * (r_raw - R_prev)
    return _clamp_r(_clamp_axiom_float(R_new))


def pathology_snapshot_dict(
    R: float,
    rmssd_star: float,
    sdnn_star: float,
    ibi_window: list[float],
    mu_L: Optional[float] = None,
    sigma_L: Optional[float] = None,
) -> dict[str, Any]:
    snap: dict[str, Any] = {
        "pathology_snapshot": {
            "R": float(R),
            "RMSSD_star": float(rmssd_star),
            "SDNN_star": float(sdnn_star),
            "ibi_last_W": [float(x) for x in ibi_window[-W_IBI:]],
        }
    }
    if mu_L is not None:
        snap["pathology_snapshot"]["mu_L"] = float(mu_L)
    if sigma_L is not None and not math.isnan(sigma_L):
        snap["pathology_snapshot"]["sigma_L"] = float(sigma_L)
    return snap


def _append_pathology_log(
    R: float,
    rmssd_star: float,
    sdnn_star: float,
    ibi_seq: list[float],
) -> None:
    _RUN_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(repr(tuple(ibi_seq[-W_IBI:])).encode("utf-8")).hexdigest()
    line = (
        f"{time.time()} R={R} RMSSD*={rmssd_star} SDNN*={sdnn_star} "
        f"IBI_SHA256={h}\n"
    )
    exists = _PATHOLOGY_LOG_FILE.is_file()
    with open(_PATHOLOGY_LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()
        os.fsync(fh.fileno())
    if not exists:
        try:
            os.chmod(_PATHOLOGY_LOG_FILE, 0o600)
        except OSError:
            pass


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


def _execute_nmi(reason: str, pathology_extra: Optional[dict[str, Any]] = None) -> None:
    pid = _read_ocbrain_pid()
    if pid is None or not _verify_omega_core_cmdline(pid):
        extra = ""
        if pathology_extra:
            extra = json.dumps(pathology_extra, sort_keys=True) + "\n"
        _write_panic_lock_atomic(f"PID_SPOOF_OR_FOREIGN\n{reason}\n{extra}")
        sys.exit(1)
    nonce = secrets.token_hex(16)
    ts = repr(time.time())
    digest = hashlib.sha256(f"{reason}|{ts}|{nonce}".encode("utf-8")).hexdigest()
    extra = ""
    if pathology_extra:
        extra = json.dumps(pathology_extra, sort_keys=True) + "\n"
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    _write_panic_lock_atomic(f"{reason}\n{digest}\n{extra}")
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


async def _measure_homeostase_latencies() -> tuple[list[float], bool]:
    """
    Feste Reihenfolge (NMI-Matrix): Status → Chroma → systemd → Postgres.
    L_p = Dauer der jeweiligen erfolgreichen Probe.
    """
    latencies: list[float] = []
    t0 = time.monotonic()
    if _http_get_code("http://localhost:8000/status") != 200:
        latencies.append(time.monotonic() - t0)
        return latencies, False
    latencies.append(time.monotonic() - t0)
    host, port = _chroma_host_port()
    t0 = time.monotonic()
    if _http_get_code(f"http://{host}:{port}/api/v1/heartbeat") != 200:
        latencies.append(time.monotonic() - t0)
        return latencies, False
    latencies.append(time.monotonic() - t0)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            ["systemctl", "is-active", "omega-event-bus"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        active = proc.stdout.strip() == "active"
    except Exception:
        active = False
    latencies.append(time.monotonic() - t0)
    if not active:
        return latencies, False
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        return latencies, False
    t0 = time.monotonic()
    pg_ok = await _postgres_select1_ok(dsn)
    latencies.append(time.monotonic() - t0)
    if not pg_ok:
        return latencies, False
    return latencies, True


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


async def _async_main() -> None:
    interval = _read_interval_sec()
    R = _clamp_r(_clamp_axiom_float(V_CAP - 0.001))
    V = _read_initial_v()
    ibi_window: deque[float] = deque(maxlen=W_IBI)
    mu_L_history: deque[float] = deque(maxlen=M_MONO)
    last_tick_end_mono: Optional[float] = None

    while True:
        latencies, homeo_ok = await _measure_homeostase_latencies()
        ibi_list = list(ibi_window)
        rmssd_star, sdnn_star = _ibi_hrv_metrics(ibi_list)
        snap_base = pathology_snapshot_dict(
            R, rmssd_star, sdnn_star, ibi_list,
            mu_L=statistics.mean(latencies) if latencies else None,
            sigma_L=statistics.stdev(latencies) if len(latencies) >= 2 else float("nan"),
        )

        if not homeo_ok:
            _execute_nmi("HOMEOSTASE_FAIL", snap_base)

        mu_L = statistics.mean(latencies)
        sigma_L = statistics.stdev(latencies) if len(latencies) >= 2 else float("nan")

        value_proof = await _evaluate_value_proof_async()
        D = _compute_D(R, rmssd_star, T_NOMINAL, PHI)
        V = _update_v_exponential(V, R, D, value_proof)
        mu_L_history.append(mu_L)
        R = _update_r_from_metrics(R, rmssd_star, T_NOMINAL, mu_L_history)

        if os.environ.get("OMEGA_PACEMAKER_INVARIANTS", "").strip() == "1":
            assert math.isfinite(V) and math.isfinite(R) and math.isfinite(D)

        if R >= PATHOLOGY_R_THRESHOLD and V < V_PATHOLOGY_CAP:
            _append_pathology_log(R, rmssd_star, sdnn_star, ibi_list)

        if V <= (LAMBDA + TOL) and not value_proof:
            full_snap = pathology_snapshot_dict(
                R, rmssd_star, sdnn_star, ibi_list, mu_L=mu_L, sigma_L=sigma_L
            )
            _execute_nmi("ASYSTOLE", full_snap)

        dbg_path = os.environ.get("OMEGA_PACEMAKER_DEBUG_METRICS_FILE", "").strip()
        if dbg_path:
            rec = {
                "V": V,
                "R": R,
                "D": D,
                "RMSSD_star": rmssd_star,
                "SDNN_star": sdnn_star,
                "ibi_n": len(ibi_list),
            }
            with open(dbg_path, "a", encoding="utf-8") as dfh:
                dfh.write(json.dumps(rec, sort_keys=True) + "\n")
                dfh.flush()

        jraw = os.environ.get("OMEGA_PACEMAKER_TEST_TICK_JITTER_SEC_MAX", "").strip()
        if jraw:
            jmax = float(jraw)
            if jmax > 0.0:
                await asyncio.sleep(secrets.SystemRandom().uniform(0.0, jmax))

        await asyncio.sleep(interval)
        tick_end = time.monotonic()
        if last_tick_end_mono is not None:
            ibi_window.append(tick_end - last_tick_end_mono)
        last_tick_end_mono = tick_end


def main() -> None:
    try:
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
