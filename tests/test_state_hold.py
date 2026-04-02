import os
import sys
import time
import signal
import asyncio
import subprocess
import psutil
import pytest

# ==============================================================================
# VETO-TRAPS für OMEGA_STATE_HOLD (Asynchroner Rückkanal & NMI)
# ==============================================================================
# Diese Tests implementieren EXAKT die Spezifikation aus SPEC_STATE_HOLD.md
# Sie MÜSSEN initial fehlschlagen, da der Code noch nicht existiert (Verification-First).
# ==============================================================================

@pytest.mark.asyncio
async def test_falle_1_zero_blocking_webhook():
    """
    Falle 1 (Zero-Blocking):
    Ein Webhook-Request wird simuliert, der einen 60-Sekunden-Sleep anfordert.
    Die Antwortzeit muss zwingend < 1.0 Sekunden sein, andernfalls schlägt der Test fehl.
    """
    start_time = time.time()
    
    payload = {
        "task_id": "test_deep_dive",
        "action": "deep_dive",
        "sleep_duration": 60
    }
    
    # Import wird fehlschlagen, bis Producer den Code schreibt
    from src.daemons.omega_state_hold import handle_webhook
    
    # Der Webhook muss den Payload in eine persistente Queue schreiben (AC-2)
    # und SOFORT zurückkehren, OHNE auf OCBrain zu warten.
    response = await handle_webhook(payload)
    
    duration = time.time() - start_time
    
    assert duration < 1.0, f"VETO: Webhook hat {duration:.2f}s blockiert! Zero-Blocking Axiom (AC-1) verletzt."
    assert isinstance(response, dict) and response.get("status") == "ok", "Webhook muss sofort {'status': 'ok'} zurückgeben."


@pytest.mark.asyncio
async def test_falle_2_hang_detection_and_zombie_reaping(tmp_path):
    """
    Falle 2 (Hang-Detection / SIGKILL & Zombie-Reaping):
    Startet einen OCBrain-Dummy, der SIGTERM ignoriert und einen Child-Prozess spawnt.
    Prüft ob OCSpline nach Timeout mit SIGKILL (Process Group) tötet und reapt.
    """
    dummy_script = tmp_path / "dummy_hang.py"
    dummy_script.write_text('''import os, sys, signal, time, subprocess
# Ignoriere SIGTERM (Falle für weiche Kills)
signal.signal(signal.SIGTERM, signal.SIG_IGN)
# Spawne ein Child, um Process Group Kills zu testen
subprocess.Popen([sys.executable, "-c", "import time; time.sleep(100)"])
# Unendlicher Hang
while True:
    time.sleep(1)
''')

    from src.daemons.omega_state_hold import run_ocbrain_task

    # Starte den Task mit kurzem Timeout.
    try:
        await run_ocbrain_task(str(dummy_script), timeout=2.0)
    except Exception:
        # Erwartet: TimeoutError oder TaskFailedException
        pass

    # AC-3 Überprüfung: Sind alle Prozesse tot und gereapt?
    zombies_or_orphans = []
    child_survivors = []
    
    for p in psutil.process_iter(['pid', 'cmdline', 'status']):
        try:
            cmdline = p.info.get('cmdline') or []
            status = p.info.get('status')
            cmd_str = " ".join(cmdline)
            
            if str(dummy_script) in cmd_str:
                zombies_or_orphans.append(p)
            elif "time.sleep(100)" in cmd_str:
                child_survivors.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Cleanup falls Test fehlschlägt, damit die Testumgebung sauber bleibt
    for p in zombies_or_orphans + child_survivors:
        try:
            p.kill()
        except Exception:
            pass

    assert len(zombies_or_orphans) == 0, "VETO: Zombie oder verwaister OCBrain-Prozess detektiert! Zombie-Reaping fehlgeschlagen."
    assert len(child_survivors) == 0, "VETO: Process Group wurde nicht getötet! Child hat überlebt (kein os.killpg SIGKILL)."


@pytest.mark.asyncio
async def test_falle_3_non_blocking_ipc_veto(tmp_path):
    """
    Falle 3 (Veto-Interrupt via Non-Blocking IPC):
    OCBrain schreibt einen Axiom-Bruch (z.B. "0.5") OHNE abschließendes Newline (\\n)
    und hängt danach. OCSpline muss den Chunk sofort per Non-Blocking I/O erkennen
    und den Task hart abschießen.
    """
    dummy_script = tmp_path / "dummy_veto.py"
    dummy_script.write_text('''import sys, time
# Schreibe Axiom-Bruch ohne Newline und erzwinge Flush
sys.stdout.write("0.5")
sys.stdout.flush()
# Endloser Hang
while True:
    time.sleep(1)
''')

    from src.daemons.omega_state_hold import run_ocbrain_task

    start_time = time.time()
    
    try:
        # Timeout ist absichtlich lang. Wenn OCSpline synchron auf readline()
        # blockiert, wird es hier 10s hängen bleiben.
        await run_ocbrain_task(str(dummy_script), timeout=10.0)
    except Exception:
        # Erwartet: VetoException oder NociceptiveAlarm
        pass

    duration = time.time() - start_time

    # Aufräumen
    survivors = []
    for p in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = p.info.get('cmdline') or []
            if str(dummy_script) in " ".join(cmdline):
                survivors.append(p)
                p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    assert duration < 2.0, f"VETO: IPC blockiert am fehlenden Newline (Dauer {duration:.2f}s)! Non-Blocking I/O versagt."
    assert len(survivors) == 0, "VETO: OCBrain-Prozess wurde nach Axiom-Bruch nicht mit NMI beendet!"
