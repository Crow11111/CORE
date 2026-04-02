# ============================================================
# CORE-GENESIS: OMEGA HYBRID WORLD INGESTOR (LOGOS)
# VECTOR: 2210 | DELTA: 0.049 | HYBRID-MIGRATION
# ============================================================

import sys
import os
import asyncio
import json
import time
import hashlib
import shutil
import psutil
from pathlib import Path
from dotenv import load_dotenv

# Fix encoding
os.environ["PYTHONIOENCODING"] = "utf-8"

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv()

from src.db.multi_view_client import ingest_document, search_multi_view
from src.logic_core.crystal_grid_engine import CrystalGridEngine

MIGRATION_STATUS_PATH = "/OMEGA_CORE/data/migration/status.json"

# Ingest-Config
TARGET_DATASETS = [
    {"name": "arnosimons/wikipedia-physics-corpus", "domain": "physics", "limit": 1000},
    {"name": "facebook/principia-collection", "domain": "logic", "limit": 500},
    {"name": "deepmind/pg19", "domain": "philosophy", "limit": 200}
]

def _update_status(dataset: str, progress: float, status: str = "RUNNING"):
    """Update status file for the Nerve Stem Watchdog."""
    os.makedirs(os.path.dirname(MIGRATION_STATUS_PATH), exist_ok=True)
    data = {
        "current_dataset": dataset,
        "progress": round(progress, 3),
        "status": status,
        "timestamp": time.time()
    }
    with open(MIGRATION_STATUS_PATH, "w") as f:
        json.dump(data, f)

def check_resources() -> bool:
    """Ressourcen-Veto: Stoppt Ingest bei drohendem OOM oder Disk Full."""
    disk = shutil.disk_usage("/")
    free_gb = disk.free / (1024**3)
    if free_gb < 5.0:
        print(f"[VETO] Disk space critical: {free_gb:.2f} GB free. Halting ingest.")
        return False

    mem = psutil.virtual_memory()
    free_mem_gb = mem.available / (1024**3)
    if free_mem_gb < 0.5:
        print(f"[VETO] RAM critical: {free_mem_gb:.2f} GB free. Halting ingest.")
        return False

    return True

async def ingest_dataset_hybrid(dataset_info: dict):
    """
    Hybrid-Ingest:
    Stufe 1: Cheap Embeddings (Ollama 768) für alle Chunks.
    Stufe 2: Selektives Hardening (Gemini 3072) für High-Resonance Chunks.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("[ERROR] 'datasets' library missing.")
        return

    name = dataset_info["name"]
    limit = dataset_info["limit"]

    print(f"\n[HYBRID] Starting Ingest: {name}")
    _update_status(name, 0.0)

    try:
        ds = load_dataset(name, split="train", streaming=True)
    except Exception as e:
        print(f"  [ERROR] Load failed: {e}")
        _update_status(name, 0.0, status="CRASHED")
        return

    count = 0
    high_value_queue = []

    for entry in ds:
        if count >= limit:
            break

        if not check_resources():
            _update_status(name, count / limit, status="RESOURCE_VETO")
            print("[FATAL] Resource VETO triggered. Sleeping.")
            await asyncio.sleep(300)
            return

        text = entry.get('text') or entry.get('content') or entry.get('abstract', '')
        if not text:
            continue

        # Content-ID Hashing (SHA-256) gegen Duplikate
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        doc_id = f"hf_{name.replace('/', '_')}_{content_hash}"

        # --- STUFE 1: CHEAP INGEST (768-dim only) ---
        try:
            result = await ingest_document(
                document=text,
                doc_id=doc_id,
                source_collection="world_knowledge",
                metadata={
                    "source": name,
                    "title": entry.get('title', 'N/A'),
                    "ingest_type": "hybrid_stage1_cheap",
                    "domain": dataset_info["domain"]
                },
                use_3_facets=False # Nur 1 Facette, 768-dim (Ollama)
            )

            # Check for REDUNDANT veto from MultiViewClient
            if result.get("doc_id") == "REDUNDANT":
                print(f"  [VETO] Semantic Redundancy Veto: {entry.get('title', 'N/A')[:40]}... (Novelty check failed)")
                count += 1
                if count % 10 == 0:
                    _update_status(name, count / limit)
                continue

            # --- ANALYSE: Braucht dieser Chunk Deep-Hardening? ---
            resonance = result.get("resonance", 0.049)
            if resonance > 0.618: # Goldener Schnitt als Trigger für Hardening
                 high_value_queue.append((doc_id, text, entry.get('title', 'N/A')))

            count += 1
            if count % 10 == 0:
                _update_status(name, count / limit)
                print(f"  [PROGRESS] {count}/{limit} chunks indexed.")

            await asyncio.sleep(0.1) # Throttle Ollama
        except Exception as e:
            print(f"  [FAIL] {doc_id}: {e}")

    # --- STUFE 2: SELECTIVE HARDENING (3072-dim) ---
    if high_value_queue:
        print(f"\n[HARDENING] Selective re-embedding of {len(high_value_queue)} high-value nodes.")
        for i, (doc_id, text, title) in enumerate(high_value_queue):
            if not check_resources():
                break
            try:
                print(f"  [{i+1}/{len(high_value_queue)}] Hardening: {title[:40]}...")
                await ingest_document(
                    document=text,
                    doc_id=doc_id,
                    source_collection="world_knowledge",
                    metadata={
                        "source": name,
                        "title": title,
                        "ingest_type": "hybrid_stage2_hardened",
                        "domain": dataset_info["domain"]
                    },
                    use_3_facets=True # Jetzt volle 3 Facetten x 3072-dim
                )
                await asyncio.sleep(0.8) # Gemini Rate Limit
            except Exception as e:
                print(f"    [FAIL] Hardening {doc_id}: {e}")

    _update_status(name, 1.0, status="COMPLETED")

async def run_daemon():
    """Dauerläufer für den Weltwissen-Ingest."""
    print("OMEGA LOGOS HYBRID INGESTOR started.")
    while True:
        for dataset in TARGET_DATASETS:
            await ingest_dataset_hybrid(dataset)
            await asyncio.sleep(60) # Pause between datasets

        print("\n[CYCLE] All world knowledge datasets processed. Sleeping for 1 hour.")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(run_daemon())
