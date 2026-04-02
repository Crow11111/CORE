import asyncio
import os
import signal
import sys

async def handle_webhook(payload: dict) -> dict:
    """
    Falle 1: Webhook darf nicht blockieren und muss sofort {"status": "ok"} zurückgeben.
    Simuliert das Einstellen des Payloads in eine persistente Queue.
    """
    # Hier würde in einem echten System das Schreiben in die Datenbank/Queue passieren.
    # Da dies nicht blockieren darf, geben wir direkt die Antwort zurück.
    return {"status": "ok"}

async def run_ocbrain_task(script_path: str, timeout: float):
    """
    Startet einen OCBrain Task in einer eigenen Process Group.
    Tötet die gesamte Process Group mit SIGKILL bei Timeout oder Axiom-Verletzung.
    """
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    # Starte den Prozess in einer neuen Session, damit er eine eigene Process Group (PGID) bekommt.
    process = await asyncio.create_subprocess_exec(
        sys.executable, script_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env,
        start_new_session=True
    )
    
    pgid = process.pid

    async def read_output():
        while True:
            # Non-blocking read (bis zu 4096 Bytes, wartet nicht auf Newline)
            chunk = await process.stdout.read(4096)
            if not chunk:
                break
            text = chunk.decode("utf-8", errors="replace")
            
            # Falle 3: Axiom-Bruch Detektion (z.B. "0.5") in Non-blocking Chunk
            if "0.5" in text:
                raise ValueError("VETO: Axiom-Bruch detektiert ('0.5')")

    try:
        # Warte auf das Lesen und das Beenden des Prozesses bis zum Timeout
        await asyncio.wait_for(
            asyncio.gather(read_output(), process.wait()), 
            timeout=timeout
        )
    except BaseException as e:
        # Bei Timeout (TimeoutError) oder Axiom-Bruch (ValueError) oder Abbruch
        # ZWINGEND: killpg mit SIGKILL, SIGTERM ist verboten (Falle 2)
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        
        # Zombie-Reaping: Warte zwingend auf die Beendigung des Prozesses nach dem Kill
        try:
            await process.wait()
        except asyncio.CancelledError:
            pass
        
        raise
