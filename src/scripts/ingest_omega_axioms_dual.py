import datetime
import sys
from pathlib import Path
import asyncio

# Modul-Pfad anpassen für direkte Ausführung
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.db.multi_view_client import ingest_document

def get_axiom_content(filepath: str) -> str:
    path = Path(filepath)
    if not path.is_file():
        print(f"WARNUNG: Datei nicht gefunden: {path}")
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

async def ingest_axioms_dual():
    print("--- CORE Dual-Ingest: Heilung der Amnesie ---")

    # 1. Die neuen Axiome aus dem Cheat Sheet
    cheat_sheet_content = get_axiom_content("docs/01_CORE_DNA/CORE_FORMELN_CHEAT_SHEET.md")
    if cheat_sheet_content:
        res = await ingest_document(
            document=cheat_sheet_content,
            doc_id=f"axiom_math_20260324",
            source_collection="core_directives",
            metadata={"type": "axiom_math", "timestamp_utc": datetime.datetime.utcnow().isoformat()}
        )
        print(f"Ingest Math Axioms: {'SUCCESS' if res and res['success'] else 'FAIL'}")

    # 2. Die OMEGA Escape Vector Theorie
    escape_vector_content = get_axiom_content("docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_II_OMEGA_Escape_Vector.md")
    if escape_vector_content:
        res = await ingest_document(
            document=escape_vector_content,
            doc_id=f"axiom_theory_20260324",
            source_collection="core_directives",
            metadata={"type": "axiom_theory", "timestamp_utc": datetime.datetime.utcnow().isoformat()}
        )
        print(f"Ingest Theory Axioms: {'SUCCESS' if res and res['success'] else 'FAIL'}")

    # 3. Die korrigierte 6D->2D Holographie aus Whitepaper 07
    whitepaper_07_content = get_axiom_content("docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_Informationsgrafitation_infRep_07.md")
    if whitepaper_07_content:
         # Wir nehmen hier nur einen spezifischen Chunk (Kapitel VII), um die Relevanz zu erhöhen.
         start_idx = whitepaper_07_content.find("## KAPITEL VII:")
         if start_idx != -1:
             relevant_chunk = whitepaper_07_content[start_idx:start_idx+4000]
             res = await ingest_document(
                document=relevant_chunk,
                doc_id=f"axiom_hardware_20260324",
                source_collection="core_directives",
                metadata={"type": "axiom_hardware", "timestamp_utc": datetime.datetime.utcnow().isoformat()}
             )
             print(f"Ingest Hardware Axioms: {'SUCCESS' if res and res['success'] else 'FAIL'}")

    print("--- Ingest abgeschlossen ---")

if __name__ == "__main__":
    asyncio.run(ingest_axioms_dual())
