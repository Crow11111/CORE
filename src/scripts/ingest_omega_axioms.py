# src/scripts/ingest_omega_axioms.py
import datetime
import sys
from pathlib import Path
import asyncio

# Modul-Pfad anpassen für direkte Ausführung
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.network.chroma_client import get_chroma_client

def get_axiom_content(filepath: str) -> str:
    path = Path(filepath)
    if not path.is_file():
        print(f"WARNUNG: Datei nicht gefunden: {path}")
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

async def ingest_axioms():
    client = await get_chroma_client()
    if not client:
        print("FEHLER: ChromaDB Client nicht verfügbar.")
        return

    collection = client.get_or_create_collection(name="core_directives")

    # 1. Die neuen Axiome aus dem Cheat Sheet
    cheat_sheet_content = get_axiom_content("docs/01_CORE_DNA/CORE_FORMELN_CHEAT_SHEET.md")

    # 2. Die OMEGA Escape Vector Theorie
    escape_vector_content = get_axiom_content("docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_II_OMEGA_Escape_Vector.md")

    # 3. Die korrigierte 6D->2D Holographie aus Whitepaper 07
    whitepaper_07_content = get_axiom_content("docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_Informationsgrafitation_infRep_07.md")

    documents = []
    metadatas = []
    ids = []

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if cheat_sheet_content:
        documents.append(cheat_sheet_content)
        metadatas.append({"source": "CORE_FORMELN_CHEAT_SHEET", "timestamp_utc": timestamp, "type": "axiom_math"})
        # Stabile IDs: Upsert ersetzt dieselben Slots, keine Duplikat-Lawine bei Re-Runs
        ids.append("axiom_math_core_directives")

    if escape_vector_content:
        documents.append(escape_vector_content)
        metadatas.append({"source": "Whitepaper_II_OMEGA_Escape_Vector", "timestamp_utc": timestamp, "type": "axiom_theory"})
        ids.append("axiom_theory_wp2_escape_vector")

    if whitepaper_07_content:
         # Wir nehmen hier nur einen spezifischen Chunk (Kapitel VII), um die Relevanz zu erhöhen.
         # Für eine vollständige Indexierung müsste ein Text-Splitter verwendet werden, aber für die Axiom-Härte
         # pushen wir den relevanten Teil direkt.
         start_idx = whitepaper_07_content.find("## KAPITEL VII:")
         if start_idx != -1:
             # Take up to 4000 characters from the start of Chapter VII
             relevant_chunk = whitepaper_07_content[start_idx:start_idx+4000]
             documents.append(relevant_chunk)
             metadatas.append({"source": "Whitepaper_07_Kapitel_VII", "timestamp_utc": timestamp, "type": "axiom_hardware"})
             ids.append("axiom_hardware_wp07_kapitel_vii")

    if documents:
        print(f"Ingesting {len(documents)} Dokumente in 'core_directives'...")
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Ingest erfolgreich.")
    else:
        print("FEHLER: Keine Dokumente zum Ingest gefunden.")

if __name__ == "__main__":
    asyncio.run(ingest_axioms())
