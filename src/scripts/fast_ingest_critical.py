import os
import sys
import asyncio
import hashlib
from pathlib import Path
from typing import List, Dict

# Add workspace root to sys.path
WORKSPACE_ROOT = Path("/OMEGA_CORE")
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.db.multi_view_client import ingest_document
from loguru import logger

# Constants
COLLECTION_NAME = "omega_root_fs"
CHUNK_SIZE = 2500 # Slightly larger for context
ALLOWED_EXTENSIONS = {".md", ".mdc", ".py", ".json", ".txt"}
# Prioritize these folders
PRIORITY_PATHS = ["docs", "src/api", "src/db", "scripts"]

async def process_file(file_path: Path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        if not content.strip():
            return 0
        
        # Simple chunking
        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]
        
        indexed_count = 0
        for i, chunk_content in enumerate(chunks):
            path_hash = hashlib.md5(str(file_path.relative_to(WORKSPACE_ROOT)).encode()).hexdigest()[:8]
            chunk_id = f"critical_{path_hash}_{i}"
            
            metadata = {
                "file_path": str(file_path.relative_to(WORKSPACE_ROOT)),
                "is_critical": True,
                "chunk_index": i
            }
            
            result = await ingest_document(
                document=chunk_content,
                doc_id=chunk_id,
                source_collection=COLLECTION_NAME,
                metadata=metadata
            )
            
            if result and result.get("success"):
                indexed_count += 1
            
            await asyncio.sleep(0.05) # Fast but safe
            
        return indexed_count
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return 0

async def main():
    logger.info("Starting FAST CRITICAL INGEST...")
    
    files_to_process = []
    
    # Collect files from priority paths
    for p in PRIORITY_PATHS:
        target_dir = WORKSPACE_ROOT / p
        if not target_dir.exists():
            continue
            
        for root, _, files in os.walk(target_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    files_to_process.append(file_path)
    
    # Also look for files with Kong or Monica in the whole root (excluding node_modules etc)
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Filter dirs
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".venv", "dist"}]
        
        for file in files:
            if "Kong" in file or "Monica" in file:
                file_path = Path(root) / file
                if file_path not in files_to_process and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    files_to_process.append(file_path)

    logger.info(f"Found {len(files_to_process)} critical files.")
    
    total_indexed = 0
    for i, file_path in enumerate(files_to_process):
        logger.info(f"[{i+1}/{len(files_to_process)}] Critical: {file_path.relative_to(WORKSPACE_ROOT)}")
        count = await process_file(file_path)
        total_indexed += count
        
    logger.info(f"Critical Ingest finished. Total chunks: {total_indexed}")

if __name__ == "__main__":
    asyncio.run(main())
