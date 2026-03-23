import os
import sys
import asyncio
from pathlib import Path

# Add workspace root to sys.path
WORKSPACE_ROOT = Path("/OMEGA_CORE")
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.db.multi_view_client import search_multi_view

async def test_search():
    print("Suche nach 'Monica' in omega_root_fs...")
    # Wir nutzen die multi_view_client Funktionalität direkt
    results = await search_multi_view("What is Monica?", limit=3, source_collection="omega_root_fs")
    if not results:
        print("Keine Ergebnisse gefunden.")
    else:
        for r in results:
            # Das psql-Parsing-Format beachten, wenn search_multi_view erfolgreich war
            print(f"\nSimilarity: {r.get('similarity', 0):.4f}")
            print(f"Doc ID: {r.get('doc_id', 'N/A')}")
            print(f"Preview: {r.get('document', '')[:300]}...")

if __name__ == "__main__":
    asyncio.run(test_search())
