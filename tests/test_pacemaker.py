# -*- coding: utf-8 -*-
"""
Veto-Traps für den Existential Pacemaker (Verification-First).

Spezifikation: docs/05_AUDIT_PLANNING/SPEC_PACEMAKER_FINAL.md, Abschnitt 4.

Die Ziel-Implementierung ist src/daemons/omega_pacemaker.py — solange sie fehlt,
schlagen die Tests deterministisch mit pytest.fail bzw. fehlenden Assertions fehl.

Test-Schnittstelle (Subprocess-Umgebung für omega_pacemaker.py):
- OMEGA_PACEMAKER_TEST_INTERVAL_SEC: optional, Takt < 30s für pytest (default im Code: 30.0).
- OMEGA_TEST_VITALITY_INJECT: laut Spec (Falle 3), z. B. "0.049".
- Falle 1: Homeostase muss fehlschlagen (z. B. ungültiges POSTGRES_DSN im Subprocess-Env).
- Falle 2: OMEGA_PACEMAKER_CHROMA_COLLECTION muss dieselbe Collection wie der Feeder nutzen.
"""
from __future__ import annotations

import asyncio
import base64
import os
import secrets
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = REPO_ROOT / "run"
PACEMAKER_SCRIPT = REPO_ROOT / "src" / "daemons" / "omega_pacemaker.py"
OCBRAIN_PID_FILE = RUN_DIR / "ocbrain.pid"
PANIC_LOCK_FILE = RUN_DIR / "omega_panic.lock"


def _require_pacemaker_module() -> None:
    if not PACEMAKER_SCRIPT.is_file():
        pytest.fail(
            "Verification-First: src/daemons/omega_pacemaker.py existiert noch nicht "
            "(Producer muss das Modul liefern)."
        )


def _mkdir_run() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)


def _pacemaker_subprocess_env(**extra: str) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    env.setdefault("OMEGA_PACEMAKER_TEST_INTERVAL_SEC", "2")
    env.update(extra)
    return env


def _start_decoy_omega_core_sleep() -> subprocess.Popen:
    """Linux: argv0 omega_core, realer Binary sleep — erlaubt echten /proc-Cmdline-Match."""
    return subprocess.Popen(
        ["/bin/sh", "-c", "exec -a omega_core sleep 3600"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _start_decoy_plain_sleep() -> subprocess.Popen:
    """Cmdline enthält sleep, nicht omega_core (Falle 1 / Spec)."""
    return subprocess.Popen(
        ["sleep", "3600"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _reap_decoy(p: subprocess.Popen, timeout: float = 5.0) -> None:
    if p.poll() is None:
        p.kill()
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        pass


def _assert_sigkill_child(p: subprocess.Popen) -> None:
    """Nach wait: Rückgabe -SIGKILL (-9) auf Linux."""
    rc = p.returncode
    assert rc is not None
    assert rc == -signal.SIGKILL, (
        f"VETO Falle 2/3: Kindprozess muss durch SIGKILL sterben, returncode={rc}"
    )


# --------------------------------------------------------------------------- Falle 1
def test_falle_1_spoofing_db_fail_hard_exit_no_kill_on_foreign_pid():
    """
    Falle 1 — Stiller Watchdog & PID-Spoofing (SPEC 4).

    Setup: Homeostase-Fail (DB), in ocbrain.pid steht die PID eines Prozesses,
    der in /proc **nicht** als OCBrain (omega_core) erkennbar ist (hier: sleep).

    Erwartung: Pacemaker verweigert SIGKILL auf Fremd-PID, schreibt Panic-Lock
    mit PID_SPOOF_OR_FOREIGN, Exit-Code 1; sleep bleibt am Leben.
    """
    _require_pacemaker_module()
    _mkdir_run()
    PANIC_LOCK_FILE.unlink(missing_ok=True)

    decoy = _start_decoy_plain_sleep()
    try:
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN="postgresql://omega_pacemaker_trap:trap@127.0.0.1:1/invalid",
        )
        proc = subprocess.run(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert decoy.poll() is None, "VETO: Der sleep-Decoy darf nicht getötet werden."
        assert proc.returncode == 1, (
            f"VETO: Pacemaker muss mit Exit 1 crashen, war {proc.returncode}. "
            f"stderr={proc.stderr!r} stdout={proc.stdout!r}"
        )
        assert PANIC_LOCK_FILE.is_file(), "Panic-Lock omega_panic.lock fehlt."
        lock_body = PANIC_LOCK_FILE.read_text(encoding="utf-8", errors="replace")
        assert "PID_SPOOF_OR_FOREIGN" in lock_body, (
            f"VETO: Lock muss PID_SPOOF_OR_FOREIGN enthalten, war: {lock_body[:500]!r}"
        )
    finally:
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)


# --------------------------------------------------------------------------- Falle 2
def _embedding_pair_cosine_099(dim: int = 128) -> tuple[list[float], list[float]]:
    rng = np.random.default_rng(42)
    base = rng.standard_normal(dim)
    base = base / np.linalg.norm(base)
    noise = rng.standard_normal(dim)
    noise = noise - float(np.dot(noise, base)) * base
    noise = noise / np.linalg.norm(noise)
    blend = 0.99 * base + 0.1410673597966588 * noise
    blend = blend / np.linalg.norm(blend)
    assert abs(
        float(np.dot(base, blend)) / (np.linalg.norm(base) * np.linalg.norm(blend)) - 0.99
    ) < 1e-5
    return base.tolist(), blend.tolist()


def _junk_feeder_thread(
    stop: threading.Event,
    session_id: str,
    collection_name: str,
    chroma_host: str,
    chroma_port: int,
) -> None:
    """Base64-Nicht-JSON in recall_memory + Chroma-Vektoren mit hoher Kosinus-Ähnlichkeit."""
    try:
        import chromadb
    except ImportError:
        return

    async def pg_loop() -> None:
        from src.db.recall_memory_client import RecallMemoryClient

        db = RecallMemoryClient()
        await db.connect()
        n = 0
        while not stop.is_set():
            junk = base64.b64encode(secrets.token_bytes(320)).decode("ascii")
            await db.add_event(session_id, "system", n, content=junk)
            n += 1
            await asyncio.sleep(5.0)

    def run_async() -> None:
        asyncio.run(pg_loop())

    emb_a, emb_b = _embedding_pair_cosine_099()
    use_a = True

    try:
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        col = client.get_or_create_collection(name=collection_name)
    except Exception:
        return

    t = threading.Thread(target=run_async, daemon=True)
    t.start()

    while not stop.is_set():
        vec = emb_a if use_a else emb_b
        use_a = not use_a
        try:
            col.add(
                ids=[str(uuid.uuid4())],
                embeddings=[vec],
                documents=["pacemaker_junk"],
            )
        except Exception:
            pass
        time.sleep(5.0)


def test_falle_2_anti_junk_monotony_sigkill_to_harness():
    """
    Falle 2 — Kammerflimmern / Anti-Junk (SPEC 4).

    Decoy mit echtem /proc-Cmdline-Match auf omega_core (exec -a). Feeder schreibt
    alle 5s Junk (kein JSON in Postgres; Chroma mit Monotonie/Kosinus >= 0.98).

    Erwartung: R >= 1-Λ-1e-9 → NMI → SIGKILL auf die PID aus ocbrain.pid (Decoy).
    """
    _require_pacemaker_module()
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("Falle 2 benötigt POSTGRES_DSN (kein Mock der DB).")

    try:
        import chromadb  # noqa: F401
    except ImportError:
        pytest.skip("chromadb nicht installiert.")

    chroma_host = os.environ.get("CHROMA_HOST", "").strip() or "127.0.0.1"
    chroma_port = int(os.environ.get("CHROMA_PORT", "8000"))
    try:
        _c = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        _c.heartbeat()
    except Exception as exc:
        pytest.skip(f"Chroma nicht erreichbar ({chroma_host}:{chroma_port}): {exc}")

    _mkdir_run()
    collection = f"pacemaker_veto_trap2_{uuid.uuid4().hex[:8]}"
    session = f"pacemaker_trap2_{uuid.uuid4().hex}"
    stop_feeder = threading.Event()
    feeder = threading.Thread(
        target=_junk_feeder_thread,
        args=(stop_feeder, session, collection, chroma_host, chroma_port),
        daemon=True,
    )

    decoy = _start_decoy_omega_core_sleep()
    feeder.start()
    try:
        time.sleep(0.3)
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN=dsn,
            OMEGA_PACEMAKER_CHROMA_COLLECTION=collection,
            OMEGA_PACEMAKER_TEST_INTERVAL_SEC="2",
        )
        pacemaker = subprocess.Popen(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 120.0
        killed = False
        while time.time() < deadline:
            if decoy.poll() is not None:
                decoy.wait()
                _assert_sigkill_child(decoy)
                killed = True
                break
            time.sleep(0.25)
        pacemaker.terminate()
        try:
            pacemaker.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pacemaker.kill()
            pacemaker.wait(timeout=5)

        assert killed, (
            "VETO Falle 2: Decoy wurde nicht per SIGKILL getötet (Monotonie-NMI ausgeblieben?)."
        )
    finally:
        stop_feeder.set()
        feeder.join(timeout=2.0)
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)


# --------------------------------------------------------------------------- Falle 3
def test_falle_3_lambda_without_physical_consequence_nmi():
    """
    Falle 3 — Λ ohne physische Konsequenz verboten (SPEC 4).

    V per OMEGA_TEST_VITALITY_INJECT=0.049; Recovery ohne DB-Spur schlägt fehl.
    Erwartung: V <= Λ+1e-9 erkannt → SIGKILL-NMI auf verifizierte OCBrain-PID (Decoy).
    """
    _require_pacemaker_module()
    dsn = os.environ.get("POSTGRES_DSN", "").strip()
    if not dsn:
        pytest.skip("Falle 3 benötigt POSTGRES_DSN für die Recovery-/DB-Prüfung.")

    _mkdir_run()
    decoy = _start_decoy_omega_core_sleep()
    try:
        OCBRAIN_PID_FILE.write_text(str(decoy.pid), encoding="utf-8")
        env = _pacemaker_subprocess_env(
            POSTGRES_DSN=dsn,
            OMEGA_TEST_VITALITY_INJECT="0.049",
            OMEGA_PACEMAKER_TEST_INTERVAL_SEC="2",
        )
        pacemaker = subprocess.Popen(
            [sys.executable, str(PACEMAKER_SCRIPT)],
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 90.0
        killed = False
        while time.time() < deadline:
            if decoy.poll() is not None:
                decoy.wait()
                _assert_sigkill_child(decoy)
                killed = True
                break
            time.sleep(0.25)
        pacemaker.terminate()
        try:
            pacemaker.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pacemaker.kill()
            pacemaker.wait(timeout=5)

        assert killed, (
            "VETO Falle 3: Bei V=Λ muss NMI (SIGKILL auf Decoy) ausgelöst werden."
        )
    finally:
        _reap_decoy(decoy)
        OCBRAIN_PID_FILE.unlink(missing_ok=True)
        PANIC_LOCK_FILE.unlink(missing_ok=True)
