import sys
import os
import asyncio
import json
import uuid
import hashlib
from pathlib import Path

# Fix encoding for shell output
os.environ["PYTHONIOENCODING"] = "utf-8"

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.multi_view_client import ingest_document, search_multi_view

async def ground_step(thought: str, action: str = "", metadata: dict = None):
    """
    Ingests an agent's cognitive step into the session_logs.
    Also searches for similar steps to ensure 'friction' and continuity.
    """
    doc_id = f"thought_{uuid.uuid4().hex[:8]}"
    
    # Construct the document
    document = f"### COGNITIVE STEP\n\n**Thought:**\n{thought}\n\n"
    if action:
        document += f"**Planned Action:**\n{action}\n"
    
    # Metadata for grounding
    meta = {
        "type": "agent_thought",
        "agent_id": "OMEGA_ORCHESTRATOR",
        "step_uuid": str(uuid.uuid4()),
        **(metadata or {})
    }
    
    # 1. Search for 'friction' (similar thoughts/decisions)
    print(f"\n[COGNITIVE] Searching for friction in DB...")
    similar = await search_multi_view(thought, limit=3, use_3_facets=True)
    
    if similar:
        print(f"[COGNITIVE] Friction found (similar patterns):")
        for i, res in enumerate(similar):
            print(f"  > {i+1}. {res['doc_id']} (sim={res['similarity']:.4f})")
    else:
        print(f"[COGNITIVE] No direct friction found. New neural path.")

    # 2. Ingest the current step
    print(f"[COGNITIVE] Ingesting thought into OMEGA memory...")
    result = await ingest_document(
        document=document,
        doc_id=doc_id,
        source_collection="session_logs",
        metadata=meta,
        use_3_facets=True
    )
    
    if result.get("success"):
        print(f"[COGNITIVE] Step stored. Conv={result.get('convergence_score'):.4f} ({result.get('convergence_level')})")
    else:
        print(f"[COGNITIVE] STORAGE FAILED.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_cognitive_step.py '<thought>' ['<action>']")
        sys.exit(1)
        
    thought_arg = sys.argv[1]
    action_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    
    asyncio.run(ground_step(thought_arg, action_arg))
