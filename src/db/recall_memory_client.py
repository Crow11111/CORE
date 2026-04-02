# -*- coding: utf-8 -*-
"""
RECALL MEMORY CLIENT: POSTGRESQL (V4)
------------------------------------
Status: PROTOTYPE | OMEGA_DB | V4
"""

import os
import json
import asyncpg
from typing import List, Dict, Any, Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

class RecallMemoryClient:
    def __init__(self):
        self.dsn = os.getenv("POSTGRES_DSN")
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(dsn=self.dsn)
                logger.info("[RECALL-DB] PostgreSQL Pool verbunden.")
            except Exception as e:
                logger.error(f"[RECALL-DB] Verbindung fehlgeschlagen: {e}")
                raise

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def add_event(self, session_id: str, role: str, turn_number: int,
                        content: str = None, tool_calls: dict = None,
                        tool_results: dict = None, metadata: dict = None):
        """Speichert ein Ereignis im Recall Memory."""
        if not self.pool: await self.connect()

        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO recall_memory (session_id, role, turn_number, content, tool_calls, tool_results, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, session_id, role, turn_number, content,
            json.dumps(tool_calls) if tool_calls else None,
            json.dumps(tool_results) if tool_results else None,
            json.dumps(metadata) if metadata else None)

    async def search_recall(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Sucht die letzten Ereignisse einer Session."""
        if not self.pool: await self.connect()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM recall_memory
                WHERE session_id = $1
                ORDER BY turn_number DESC
                LIMIT $2
            """, session_id, limit)
            return [dict(r) for r in rows]

# Singleton
recall_db = RecallMemoryClient()
