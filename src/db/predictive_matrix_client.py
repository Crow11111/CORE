# -*- coding: utf-8 -*-
"""
PREDICTIVE MATRIX CLIENT (V4)
----------------------------
Status: PROTOTYPE | OMEGA_DB | V4
Implementiert das Precision Weighting gemäß Free Energy Principle.
"""

import os
import hashlib
from typing import Optional, Dict, Any
from loguru import logger
from .recall_memory_client import recall_db

class PredictiveMatrixClient:
    def __init__(self):
        self.client = recall_db # Nutzt denselben Pool

    def _generate_trigger_hash(self, intent: str, context: str) -> str:
        """Erzeugt einen stabilen Hash für eine Intent-Kontext-Paarung."""
        base = f"{intent}_{context[:100]}"
        return hashlib.sha256(base.encode()).hexdigest()

    async def get_weights(self, intent: str, context: str) -> Dict[str, float]:
        """
        Holt die aktuellen Gewichte für eine Aktion.
        Default: a_priori_weight = 0.951 (Resonance Lock)
        """
        trigger_hash = self._generate_trigger_hash(intent, context)
        if not self.client.pool: await self.client.connect()
        
        async with self.client.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT a_priori_weight, ex_post_delta 
                FROM predictive_matrix 
                WHERE trigger_hash = $1
                ORDER BY created_at DESC LIMIT 1
            """, trigger_hash)
            
            if row:
                return {
                    "a_priori_weight": float(row["a_priori_weight"]),
                    "ex_post_delta": float(row["ex_post_delta"])
                }
            
            # Default-Werte: Cold Start bei 0.51 (Axiom A5 Neutraler Bruch)
            return {"a_priori_weight": 0.51, "ex_post_delta": 0.49}

    async def update_matrix(self, intent: str, context: str, a_priori_weight: float, ex_post_delta: float):
        """Speichert die neue Erfahrung in der Matrix."""
        trigger_hash = self._generate_trigger_hash(intent, context)
        if not self.client.pool: await self.client.connect()
        
        async with self.client.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO predictive_matrix (trigger_hash, a_priori_weight, ex_post_delta)
                VALUES ($1, $2, $3)
            """, trigger_hash, a_priori_weight, ex_post_delta)
            logger.debug(f"[PREDICTIVE-MATRIX] Update: {intent} -> Weight: {a_priori_weight:.3f}, Delta: {ex_post_delta:.3f}")

# Singleton
predictive_matrix = PredictiveMatrixClient()
