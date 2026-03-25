
import asyncio
import os
import sys
import uuid
import re
import json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.multi_view_client import (
    _run_pg_sql,
    embed_3_facets,
    convergence_score,
    insert_multi_view,
    FACET_TO_COLLECTION,
    _multiview_ssh_config
)
from src.network import chroma_client

load_dotenv()

async def _run_pg_sql_raw(sql: str) -> tuple[bool, str]:
    """Run SQL with --no-align --field-separator '|' --tuples-only for easier parsing."""
    import subprocess
    key, host, user, docker_cmd = _multiview_ssh_config()
    # Add flags to docker command for raw output
    docker_cmd_raw = docker_cmd.replace("psql", "psql --no-align --field-separator '|' --tuples-only")
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
        "-i", key, f"{user}@{host}", docker_cmd_raw,
    ]
    try:
        def _run():
            return subprocess.run(
                ssh_cmd,
                input=sql.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )
        result = await asyncio.to_thread(_run)
        out = (result.stdout or b"").decode("utf-8", errors="replace")
        return result.returncode == 0, out
    except Exception as e:
        return False, str(e)

async def migrate():
    logger.info("Starting Migration: Legacy PG -> ChromaDB (3-Facets)")

    # 1. Fetch only IDs first
    sql_ids = "SELECT doc_id FROM multi_view_embeddings WHERE v_math IS NOT NULL LIMIT 50;"
    ok, out = await _run_pg_sql_raw(sql_ids)
    if not ok:
        logger.error("Failed to fetch IDs from PG")
        return

    doc_ids = [line.strip() for line in out.splitlines() if line.strip()]
    if not doc_ids:
        logger.error(f"No IDs found in output: {out[:200]}...")
        return

    logger.info(f"Processing batch of {len(doc_ids)} doc_ids")

    for doc_id in doc_ids:
        # 2. Fetch full document for this ID
        sql_fetch = f"SELECT document, source_collection, metadata FROM multi_view_embeddings WHERE doc_id = '{doc_id}' LIMIT 1;"
        ok, out = await _run_pg_sql_raw(sql_fetch)
        if not ok:
            logger.error(f"Failed to fetch document {doc_id}")
            continue

        parts = out.split('|')
        if len(parts) < 3:
            logger.error(f"Could not parse row for {doc_id}: {out[:100]}...")
            continue

        document = parts[0].strip()
        source = parts[1].strip()
        meta_s = parts[2].strip()
        try:
            meta = json.loads(meta_s)
        except:
            meta = {}

        # AI-Skepsis: is_ai Flag setzen
        if meta.get("speaker") == "gemini":
            meta["is_ai"] = True

        logger.info(f"Migrating {doc_id} (is_ai={meta.get('is_ai', False)})...")

        # Generate 3-Facets
        # Note: embed_3_facets and insert_multi_view now include the BIAS_DAMPER
        vectors = await embed_3_facets(document)
        if not vectors:
            logger.warning(f"Failed to generate embeddings for {doc_id}")
            continue

        score, pairs = convergence_score(vectors)

        # Update/Insert
        success = await insert_multi_view(
            doc_id=doc_id,
            document=document,
            vectors=vectors,
            score=score,
            pairs=pairs,
            source_collection=source,
            metadata=meta
        )

        if success:
            logger.info(f"Successfully migrated {doc_id}")
        else:
            logger.error(f"Failed to migrate {doc_id}")

if __name__ == "__main__":
    asyncio.run(migrate())
