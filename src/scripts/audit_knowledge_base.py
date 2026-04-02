import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.network.chroma_client import get_collection

async def audit():
    collections = [
        'mv_keywords', 'mv_semantics', 'mv_media',
        'session_logs', 'knowledge_graph',
        'core_directives', 'simulation_evidence',
        'world_knowledge'
    ]
    print("=== OMEGA KNOWLEDGE BASE AUDIT ===")
    total_docs = 0
    for c_name in collections:
        try:
            col = await get_collection(c_name)
            count = col.count()
            total_docs += count
            print(f"[{c_name:20}] : {count:5} Dokumente")
        except Exception as e:
            print(f"[{c_name:20}] : OFFLINE ({e})")

    print("-" * 40)
    print(f"TOTAL REGISTERED WISDOM  : {total_docs} Dokumente")

    if total_docs < 500:
        print("\n[WARNUNG] Das Gehirn ist fast leer. Wir operieren im Vakuum.")
    else:
        print("\n[STATUS] Grundrauschen vorhanden. Reibung möglich.")

if __name__ == "__main__":
    asyncio.run(audit())
