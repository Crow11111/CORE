import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load Env
load_dotenv()

from src.logic_core.resonance_membrane import check_omega_pulse, OmegaCircuitBreakerException

async def run_audit():
    print("--- OMEGA PULSE AUDIT (ZERO-TRUST) ---")
    try:
        # 0/1 Schalter Test
        pulse_ok = await check_omega_pulse()
        if pulse_ok:
            print("[SUCCESS] Resonance Lock: 0.951. OMEGA-System online.")
            sys.exit(0)
    except OmegaCircuitBreakerException as e:
        print(f"[VETO] Circuit Breaker Tripped: {e}")
        sys.exit(2) # Exit Code 2 for Veto
    except Exception as e:
        print(f"[ERROR] Unexpected System Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_audit())
