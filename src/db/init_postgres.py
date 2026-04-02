# -*- coding: utf-8 -*-
"""
POSTGRESQL INITIALIZATION (V4)
------------------------------
Status: PRODUCTIVE | OMEGA_DB | V4
"""

import os
import asyncio
from src.db.multi_view_client import _run_pg_sql
from loguru import logger

async def init_db():
    sql_path = "/OMEGA_CORE/src/db/init_postgres.sql"
    if not os.path.exists(sql_path):
        logger.error(f"SQL Datei nicht gefunden: {sql_path}")
        return

    with open(sql_path, "r") as f:
        sql = f.read()

    logger.info("[DB-INIT] Führe init_postgres.sql auf VPS aus...")
    ok, out = await _run_pg_sql(sql)
    
    if ok:
        logger.info("[DB-INIT] Erfolg: Tabellen und Indizes erstellt.")
        print(out)
    else:
        logger.error(f"[DB-INIT] Fehler bei DB-Initialisierung: {out}")

if __name__ == "__main__":
    asyncio.run(init_db())
