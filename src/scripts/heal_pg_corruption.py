
import asyncio
import os
import sys
import re
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.multi_view_client import _run_pg_sql

load_dotenv()

async def heal_pg():
    logger.info("Healing corrupted documents in PostgreSQL (vertical layout corruption)")
    # Re-using the SQL logic from the ND-Analyst
    sql_heal = "UPDATE multi_view_embeddings SET document = regexp_replace(document, E'(\\n\\s*)+', ' ', 'g') WHERE length(document) > 50 AND (length(document) - length(replace(document, chr(10), ''))) > (length(document) / 5) AND source_collection = 'omega_root_fs';"

    ok, out = await _run_pg_sql(sql_heal)
    if ok:
        logger.info(f"Heal SUCCESS: {out}")
    else:
        logger.error(f"Heal FAILED: {out}")

if __name__ == "__main__":
    asyncio.run(heal_pg())
