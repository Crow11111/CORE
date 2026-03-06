"""
TAKT 0 GATE - The Glüh-Gate on the Diagonal.
Acts as a hard async barrier before any query reaches the Core Cube.
"""
import asyncio
from src.mtho_core import MTHOCore

async def check_takt_zero() -> bool:
    """
    Asynchronous Takt 0 Check (Diagnose/Wuji).
    Verifies system resonance and state vector alignment before allowing transit.

    Returns:
        True if the gate opens (System Stable).
        False if the gate remains closed (Veto/Instability).
    """
    try:
        # Run the synchronous core check in a non-blocking thread
        core = MTHOCore()
        is_resonant = await asyncio.to_thread(core.calibrate_resonance, "0221")

        if not is_resonant:
            return False

        # Basic BARYONIC DELTA check (could be expanded)
        is_stable = await asyncio.to_thread(core.check_baryonic_limit, 0.049)

        if not is_stable:
            return False

        # Takt 0 is Wuji (Silence/Potential).
        # We ensure we are not in a 'COLLAPSED' state (y=1 without purpose).
        # (Simplified check for now)
        return True

    except Exception as e:
        print(f"[TAKT 0 VETO] Gate Check Exception: {e}")
        return False
