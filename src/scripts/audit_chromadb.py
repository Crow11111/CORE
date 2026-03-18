import os
import sys
import asyncio

# Ensure correct encoding for Windows PowerShell output
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv("/OMEGA_CORE/.env")
sys.path.append("/OMEGA_CORE")

from src.network.chroma_client import (
    get_chroma_client,
    COLLECTION_KNOWLEDGE_GRAPH,
    COLLECTION_CORE_BRAIN,
    COLLECTION_KRYTO_SCAN,
    COLLECTION_EVENTS,
    COLLECTION_INSIGHTS,
    COLLECTION_SESSION_LOGS,
    COLLECTION_CORE_DIRECTIVES,
    COLLECTION_SIMULATION_EVIDENCE,
    COLLECTION_CONTEXT,
    COLLECTION_WORLD_KNOWLEDGE
)

collections_to_check = [
    COLLECTION_KNOWLEDGE_GRAPH,
    COLLECTION_CORE_BRAIN,
    COLLECTION_KRYTO_SCAN,
    COLLECTION_EVENTS,
    COLLECTION_INSIGHTS,
    COLLECTION_SESSION_LOGS,
    COLLECTION_CORE_DIRECTIVES,
    COLLECTION_SIMULATION_EVIDENCE,
    COLLECTION_CONTEXT,
    COLLECTION_WORLD_KNOWLEDGE
]

async def audit_chroma():
    print("==================================================")
    print("CORE CHROMA-DB AUDIT (HARDWARE REALITY CHECK)")
    print("==================================================")

    try:
        client = await get_chroma_client()
        print(f"Client verbunden. Remote: {bool(os.getenv('CHROMA_HOST'))}")

        total_docs = 0
        for name in collections_to_check:
            try:
                col = client.get_collection(name=name)
                count = col.count()
                total_docs += count
                print(f"[OK] Collection '{name}': {count} Vektoren")

                # Wenn Dokumente vorhanden, ziehe einen echten Datenpunkt
                if count > 0 and name == COLLECTION_CORE_DIRECTIVES:
                    sample = col.get(limit=1, include=["documents", "metadatas"])
                    if sample and sample["documents"]:
                        print(f"     -> [BEWEIS-DATENSATZ {name}]: {sample['documents'][0][:150]}...")
                elif count > 0 and name == COLLECTION_SIMULATION_EVIDENCE:
                    sample = col.get(limit=1, include=["documents", "metadatas"])
                    if sample and sample["documents"]:
                        print(f"     -> [BEWEIS-DATENSATZ {name}]: {sample['documents'][0][:150]}...")
            except ValueError:
                print(f"[--] Collection '{name}': Nicht existent (0 Vektoren)")
            except Exception as e:
                print(f"[!!] Fehler bei Collection '{name}': {e}")

        print("==================================================")
        print(f"GESAMT-VEKTOREN IM SYSTEM: {total_docs}")
        print("==================================================")

    except Exception as e:
        print(f"KRITISCHER FEHLER BEIM CHROMA-ZUGRIFF: {e}")

if __name__ == "__main__":
    asyncio.run(audit_chroma())
