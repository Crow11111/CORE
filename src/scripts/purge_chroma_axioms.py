import asyncio
import os
from src.network.chroma_client import get_collection

async def purge_axioms():
    print("[PURGE] Lade core_directives Collection...")
    try:
        col = await get_collection("core_directives")
        if col:
            results = col.get()
            ids = results.get("ids", [])
            if ids:
                print(f"[PURGE] Lösche {len(ids)} Axiome aus ChromaDB...")
                col.delete(ids=ids)
                print("[PURGE] Erfolg: core_directives geleert.")
            else:
                print("[PURGE] Keine Axiome gefunden.")
        else:
            print("[PURGE] Collection core_directives existiert nicht.")
    except Exception as e:
        print(f"[PURGE] Fehler: {e}")

if __name__ == "__main__":
    asyncio.run(purge_axioms())
