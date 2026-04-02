import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Fix encoding
os.environ["PYTHONIOENCODING"] = "utf-8"

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv()

from src.agents.core_agent import EphemeralAgentPool, IntentType

async def test_handler(payload):
    print("  [TEST-HANDLER] Executing...")
    grounding = payload.get("_grounding_context", [])
    print(f"  [TEST-HANDLER] Found {len(grounding)} contextual memories.")
    for g in grounding:
        doc_str = str(g.get("document", ""))[:150]
        score = g.get("similarity", 0)
        source = g.get("metadata", {}).get("source", "UNKNOWN")
        print(f"    -> [Sim={score:.4f} | Src={source}] {doc_str.replace(chr(10), ' ')}")
    return {"status": "Test successful", "memory_count": len(grounding)}

async def main():
    print("\n--- OMEGA VOLLKREIS-VALIDIERUNG (OHNE GEDÄCHTNIS) ---")
    pool = EphemeralAgentPool()
    pool.register_handler(IntentType.COMMAND, test_handler)

    print("\n[STEP 1] Spawning Ephemeral Agent (Intent: COMMAND)")
    payload = {"query": "Was ist das fundamentale Axiom der OMEGA-Architektur? Wie sieht der Status der VPS-Migration aus?"}

    agent = await pool.spawn(IntentType.COMMAND, payload)
    result = await pool.execute(agent)

    print("\n[STEP 2] Agent Result:")
    print(f"  Success: {result.success}")
    if result.success:
        print(f"  Duration: {result.duration_ms:.2f}ms")
        print(f"  Output: {result.payload}")
    else:
        print(f"  Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(main())
