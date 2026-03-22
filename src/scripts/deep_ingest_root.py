import os
import sys
import asyncio
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add workspace root to sys.path
WORKSPACE_ROOT = Path("/OMEGA_CORE")
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.db.multi_view_client import ingest_document, search_multi_view
from loguru import logger

# Constants
COLLECTION_NAME = "omega_core_funnel"
CHUNK_SIZE = 1500 # Etwas kleiner fuer praezisere Linsen
EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build", "mcps", "terminals", "backups"}
ALLOWED_EXTENSIONS = {
    ".md", ".py", ".js", ".ts", ".tsx", ".jsx", 
    ".json", ".yaml", ".yml", ".mdc", ".sty", ".sql"
}
PRIORITY_KEYWORDS = ["Dreadnought", "Scout", "Monica", "Kong", "OC Brain", "OpenClaw"]
DELAY_BETWEEN_CHUNKS = 0.2

def get_file_metadata(file_path: Path) -> Dict:
    stat = file_path.stat()
    return {
        "file_path": str(file_path.relative_to(WORKSPACE_ROOT)),
        "file_type": file_path.suffix.lstrip("."),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "file_size": stat.st_size
    }

def chunk_text(text: str, size: int) -> List[str]:
    """Simple character-based chunking with paragraph awareness."""
    if len(text) <= size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        last_newline = text.rfind("\n", start, end)
        if last_newline != -1 and last_newline > start + (size // 2):
            end = last_newline
        
        chunks.append(text[start:end].strip())
        start = end
        
    return [c for c in chunks if c.strip()]

async def process_file(file_path: Path) -> int:
    try:
        metadata_base = get_file_metadata(file_path)
        is_priority = any(kw.lower() in str(file_path).lower() for kw in PRIORITY_KEYWORDS)
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        if not content.strip():
            return 0
            
        if any(kw.lower() in content.lower() for kw in PRIORITY_KEYWORDS):
            is_priority = True
            
        chunks = chunk_text(content, CHUNK_SIZE)
        indexed_count = 0
        for i, chunk_content in enumerate(chunks):
            path_hash = hashlib.md5(metadata_base["file_path"].encode()).hexdigest()[:8]
            chunk_id = f"core_{path_hash}_{i}"
            
            metadata = metadata_base.copy()
            metadata["chunk_index"] = i
            metadata["total_chunks"] = len(chunks)
            metadata["is_priority"] = is_priority
            metadata["ingest_time"] = datetime.now().isoformat()
            
            result = await ingest_document(
                document=chunk_content,
                doc_id=chunk_id,
                source_collection=COLLECTION_NAME,
                metadata=metadata
            )
            
            if result and result.get("success"):
                indexed_count += 1
            
            await asyncio.sleep(DELAY_BETWEEN_CHUNKS) 
            
        return indexed_count
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return 0

async def main():
    logger.info(f"Starting TRICHTER (Funnel) deep root ingest of {WORKSPACE_ROOT}...")
    
    total_files = 0
    total_indexed_documents = 0
    
    files_to_process = []
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                files_to_process.append(file_path)
    
    def sort_key(p: Path):
        score = 0
        if any(kw.lower() in str(p).lower() for kw in PRIORITY_KEYWORDS):
            score -= 1000
        if "docs" in str(p):
            score -= 500
        return score

    files_to_process.sort(key=sort_key)
    logger.info(f"Found {len(files_to_process)} candidate files. Priority first.")
    
    for i, file_path in enumerate(files_to_process):
        rel_path = file_path.relative_to(WORKSPACE_ROOT)
        logger.info(f"[{i+1}/{len(files_to_process)}] Processing {rel_path}...")
        count = await process_file(file_path)
        total_indexed_documents += count
        if count > 0:
            total_files += 1
            
    logger.info(f"Deep Ingest finished. Files: {total_files}, Total Chunks: {total_indexed_documents}")
    
    logger.info("Running verification query: 'What is Monica?'")
    results = await search_multi_view("What is Monica?", limit=5, source_collection=COLLECTION_NAME, use_3072=True)
    
    print("\n" + "="*60)
    print("VERIFICATION RESULTS: 'What is Monica?'")
    print("="*60)
    if not results:
        print("No results found.")
    for r in results:
        print(f"\nSimilarity: {r.get('similarity', 0):.4f} | Source: {r.get('source', 'N/A')}")
        print(f"Doc ID: {r.get('doc_id', 'N/A')}")
        print(f"Preview: {r.get('document', '')[:300]}...")

    print("\n" + "="*60)
    print(f"ERLEDIGT: {total_indexed_documents} Dokumente (Chunks) aus {total_files} Dateien indiziert.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
