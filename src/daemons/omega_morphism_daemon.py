"""
CORE SYSTEM PROTOCOL (LAYER 0)
OMEGA MORPHISM DAEMON
Delta: 0.049
"""
import asyncio
import logging
import json
import os
import uuid
import numpy as np
import asyncpg
from src.network.chroma_client import get_collection

logger = logging.getLogger("omega_morphism_daemon")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

BARYONIC_DELTA = 0.049
TICK_INTERVAL = 13.049

def compute_ptl_spectrum(vectors: list[list[float]]) -> list[float]:
    """
    Mock für Persistent Combinatorial Laplacians (PTL).
    Ersetzt np.mean Echtzeit-Routing durch topologische Verdichtung.
    """
    if not vectors:
        return [BARYONIC_DELTA] * 768

    arr = np.array(vectors)
    
    # Dummy: Gewichtete Dichte-Berechnung (wichtet neuere Vektoren höher)
    weights = np.linspace(BARYONIC_DELTA, 1.0, len(arr))
    weights /= weights.sum()
    
    weighted_sum = np.average(arr, axis=0, weights=weights)
    
    # Topologische Kompression (Non-linear)
    anchor = np.tanh(weighted_sum)
    
    # 768-Dim Forcing
    if len(anchor) > 768:
        anchor = anchor[:768]
    elif len(anchor) < 768:
        anchor = np.pad(anchor, (0, 768 - len(anchor)), constant_values=BARYONIC_DELTA)
        
    return anchor.tolist()

async def fetch_recent_vectors() -> list[list[float]]:
    """Liest die letzten 100 Vektoren aus PostgreSQL (pgvector)."""
    vectors = []
    pg_dsn = os.getenv("DATABASE_URL", "postgres://atlas_admin:password@localhost:5432/atlas_state")
    
    try:
        # Asymmetrischer Timeout
        conn = await asyncpg.connect(pg_dsn, timeout=5.049)
        try:
            # Nutzt Legacy-768-Spalte für TDA
            rows = await conn.fetch('''
                SELECT v_philo_768 
                FROM multi_view_embeddings 
                WHERE v_philo_768 IS NOT NULL 
                LIMIT 100
            ''')
            
            for row in rows:
                vec_str = row['v_philo_768']
                if isinstance(vec_str, str):
                    vectors.append(json.loads(vec_str))
                elif isinstance(vec_str, list):
                    vectors.append(vec_str)
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"[DB-FETCH] Veto: {e}")
        
    return vectors

async def push_to_chroma(anchor_vector: list[float]):
    """Pusht den kondensierten Anker in ChromaDB."""
    try:
        col = await get_collection("mv_semantics_toss")
        anchor_id = f"ptl-anchor-{uuid.uuid4().hex[:12]}"
        
        await asyncio.to_thread(
            col.upsert,
            ids=[anchor_id],
            embeddings=[anchor_vector],
            metadatas=[{
                "type": "ptl_spectrum",
                "dimension": 768,
                "delta_compliance": True
            }]
        )
        logger.info(f"[CHROMA-PUSH] Topologischer Anker gesichert: {anchor_id}")
    except Exception as e:
        logger.error(f"[CHROMA-PUSH] Veto: {e}")

async def morphism_worker():
    """Endlos-Schleife (Asynchroner TDA-Worker)."""
    logger.info("Omega Morphism Daemon initialisiert. (Delta: 0.049)")
    
    while True:
        try:
            vectors = await fetch_recent_vectors()
            
            if len(vectors) > 1:
                anchor_vector = compute_ptl_spectrum(vectors)
                await push_to_chroma(anchor_vector)
            else:
                logger.warning("[TAKTIK] Ungenügende Vektor-Dichte für PTL-Spektrum. Überspringe Takt.")
                
        except asyncio.CancelledError:
            logger.info("Morphism Daemon terminiert.")
            break
        except Exception as e:
            logger.error(f"[WORKER-ERROR] System-Anomalie: {e}")
            
        await asyncio.sleep(TICK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(morphism_worker())
    except KeyboardInterrupt:
        logger.info("Manuelle Terminierung erkannt.")
