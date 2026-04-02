import sys
import os
import asyncio
import hashlib
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.db.multi_view_client import ingest_document

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

async def process_file(file_path_str: str):
    """Reads and ingests a single file."""
    file_path = PROJECT_ROOT / file_path_str
    if not file_path.exists() or not file_path.is_file():
        return

    rel_path = file_path.relative_to(PROJECT_ROOT)
    parts = rel_path.parts
    if len(parts) > 1:
        collection_name = f"core_{parts[0]}"
    else:
        collection_name = "core_root"

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
                    "ingest_type": "recent_updates_scan"
                },
                use_3_facets=True
            )
            await asyncio.sleep(DELAY_BETWEEN_CHUNKS)
        except Exception as e:
            print(f"\n    [FAIL] {chunk['chunk_id']}: {e}")
    print(f"\n  [DONE] {rel_path}")

async def run_recent_ingest():
    print("=== OMEGA RECENT-UPDATES INGEST ===")

    try:
        # Finde alle geänderten/neuen Dateien in den letzten 31 Commits
        # (die Anzahl der Commits, die wir gerade gepusht haben)
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~31", "HEAD"],
            capture_output=True, text=True, check=True
        )
        changed_files = result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git diff fehlgeschlagen: {e}")
        return

    files_to_process = [f for f in changed_files if f.endswith('.py') or f.endswith('.md')]

    print(f"[FOUND] {len(files_to_process)} relevante .py/.md Dateien aus den letzten 31 Commits.")

    for i, file_path_str in enumerate(files_to_process):
        print(f"\n--- FILE {i+1}/{len(files_to_process)} ---")
        await process_file(file_path_str)

if __name__ == "__main__":
    asyncio.run(run_recent_ingest())
