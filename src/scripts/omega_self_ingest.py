import sys
import os
import asyncio
import hashlib
from pathlib import Path
from dotenv import load_dotenv

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.db.multi_view_client import ingest_document

# Configuration
IGNORE_DIRS = {".git", ".venv", "__pycache__", "node_modules", "dist", "build"}
FILE_EXTENSIONS = {".py", ".md"}
CHUNK_MIN_CHARS = 300
CHUNK_MAX_CHARS = 4000
DELAY_BETWEEN_CHUNKS = 0.2

def chunk_text(text: str, source_id: str) -> list[dict]:
    """Simple paragraph-based chunker."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) > CHUNK_MAX_CHARS and len(current) >= CHUNK_MIN_CHARS:
            chunk_hash = hashlib.md5(current[:200].encode()).hexdigest()[:12]
            chunks.append({
                "text": current.strip(),
                "chunk_id": f"{source_id}_{chunk_hash}"
            })
            current = para
        else:
            current += "\n\n" + para if current else para

    if current.strip() and len(current.strip()) >= CHUNK_MIN_CHARS:
        chunk_hash = hashlib.md5(current[:200].encode()).hexdigest()[:12]
        chunks.append({
            "text": current.strip(),
            "chunk_id": f"{source_id}_{chunk_hash}"
        })

    return chunks

async def process_file(file_path: Path):
    """Reads and ingests a single file."""
    rel_path = file_path.relative_to(PROJECT_ROOT)
    # Collection name based on top-level dir (src, docs, root)
    parts = rel_path.parts
    if len(parts) > 1:
        collection_name = f"core_{parts[0]}"
    else:
        collection_name = "core_root"

    # doc_id is the relative path (sanitized)
    doc_id_base = str(rel_path).replace("/", "_").replace(".", "_")

    print(f"\n[PROCESS] {rel_path} -> {collection_name}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERROR] Could not read {file_path}: {e}")
        return

    chunks = chunk_text(content, doc_id_base)
    print(f"  [INFO] {len(chunks)} Chunks generated.")

    for i, chunk in enumerate(chunks):
        try:
            print(f"    [{i+1}/{len(chunks)}] Ingesting {chunk['chunk_id']}...", end="\r")
            await ingest_document(
                document=chunk["text"],
                doc_id=chunk["chunk_id"],
                source_collection=collection_name,
                metadata={
                    "file_path": str(rel_path),
                    "file_type": file_path.suffix,
                    "ingest_type": "self_aware_scan"
                },
                use_3_facets=True
            )
            await asyncio.sleep(DELAY_BETWEEN_CHUNKS)
        except Exception as e:
            print(f"\n    [FAIL] {chunk['chunk_id']}: {e}")
    print(f"\n  [DONE] {rel_path}")

async def run_self_ingest():
    """Finds all relevant files and starts ingestion."""
    print("=== OMEGA SELF-AWARENESS INGEST (VOLLKREIS) ===")

    files_to_process = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            path = Path(root) / file
            if path.suffix in FILE_EXTENSIONS:
                files_to_process.append(path)

    print(f"[FOUND] {len(files_to_process)} Files to index.")

    for i, file_path in enumerate(files_to_process):
        print(f"\n--- FILE {i+1}/{len(files_to_process)} ---")
        await process_file(file_path)

if __name__ == "__main__":
    asyncio.run(run_self_ingest())
