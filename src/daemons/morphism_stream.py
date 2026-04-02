# -*- coding: utf-8 -*-
r"""
OMEGA MORPHISM STREAM (REAL-TIME STATE SYNC)
-------------------------------------------
Ersatz für diskreten Git-Sync durch kontinuierliche Funktor-Morphismen.
Implementiert kategoriale Homotopie zur Zustands-Synchronisation zwischen
Dreadnought (Local), VPS (Remote) und Scout (Hardware).

Axiom: G(f) ∘ \alpha_X = \alpha_Y ∘ F(f) (Kommutativität)
"""

import asyncio
import json
import logging
import time
import uuid
import sys
import os
import numpy as np
import websockets
from typing import Dict, Any, List, Optional, Set
from loguru import logger

# Project Imports
sys.path.append(os.getcwd())
from src.logic_core.projection_layer import projection_horizon
from src.logic_core.resonance_membrane import assert_resonance_float, assert_infrastructure_int
from src.config.core_state import BARYONIC_DELTA

class MorphismStream:
    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # State Storage: Dict[category, vector]
        # Initial 6D State (S, P, I, R, Z, G)
        self.system_state: Dict[str, np.ndarray] = {
            "CORE": np.array([0.51, 0.49, 0.51, 0.49, 0.51, 0.49]) 
        }
        
        # Commutativity Cache (für Latenz-Korrektur)
        self.history: List[Dict[str, Any]] = []
        self.MAX_HISTORY = 137 # Feigenbaum-Konstante / Alpha-Resonanz
        
    async def handler(self, websocket):
        """WebSocket connection handler."""
        self.clients.add(websocket)
        logger.info(f"[MORPHISM] Client connected: {websocket.remote_address}. Active: {len(self.clients)}")
        
        try:
            # Sende initialen State zur Synchronisation
            await websocket.send(json.dumps({
                "type": "INITIAL_STATE",
                "payload": {k: v.tolist() for k, v in self.system_state.items()},
                "timestamp": time.time()
            }))
            
            async for message in websocket:
                await self.handle_message(message, websocket)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logger.info(f"[MORPHISM] Client disconnected. Active: {len(self.clients)}")

    async def broadcast_morphism(self, category: str, new_vector: np.ndarray, source: str = "DREADNOUGHT"):
        """Berechnet die natürliche Transformation und broadcastet sie."""
        old_vector = self.system_state.get(category, np.zeros_like(new_vector))
        
        if old_vector.shape != new_vector.shape:
            # Fallback bei Dimensionswechsel (z.B. TOSS Injektion)
            old_vector = np.zeros_like(new_vector) + BARYONIC_DELTA

        # Natürliche Transformation via Projection Layer
        alpha = projection_horizon.calculate_natural_transformation(old_vector, new_vector)
        
        # State Update (Persistenz im RAM)
        self.system_state[category] = new_vector
        
        morphism_packet = {
            "type": "NATURAL_TRANSFORMATION",
            "category": category,
            "morphism": alpha.tolist(),
            "target_state": new_vector.tolist(),
            "source": source,
            "timestamp": time.time(),
            "morphism_id": str(uuid.uuid4())
        }
        
        # In Historie einrasten (Homotopie-Pfad)
        self.history.append(morphism_packet)
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)
            
        if self.clients:
            message = json.dumps(morphism_packet)
            # Paralleler Broadcast
            await asyncio.gather(*[client.send(message) for client in self.clients], return_exceptions=True)
            logger.debug(f"[MORPHISM] Broadcasted {category} shift from {source}. Alpha-Norm: {np.linalg.norm(alpha):.4f}")

    async def handle_message(self, message_str: str, source_ws):
        """Verarbeitet eingehende Transformationen von VPS oder Scout."""
        try:
            data = json.loads(message_str)
            m_type = data.get("type")
            
            if m_type == "PUSH_STATE":
                category = data["category"]
                payload = np.array(data["payload"])
                
                # Validierung der Membran (Axiom Check)
                if category == "CORE":
                    for val in payload: 
                        # Wir nutzen den Realteil für den Axiom-Check
                        check_val = val.real if isinstance(val, complex) else val
                        if abs(check_val - 0.5) < 0.001 or check_val in [0.0, 1.0]:
                            logger.warning(f"[MORPHISM] Veto: Ungültiger Wert {val} in Kategorie {category}")
                            return

                await self.broadcast_morphism(category, payload, source="REMOTE_PUSH")
                
        except Exception as e:
            logger.error(f"[MORPHISM] Error handling message: {e}")

    async def run(self):
        logger.info(f"[MORPHISM] Starting Stream Server on {self.host}:{self.port}...")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # run forever

# --- GLOBAL INTERFACE ---
# morphism_stream = MorphismStream() # ENTFERNT. DIES WIRD NICHT MEHR GLOBAL BENÖTIGT


async def push_morphism(category: str, new_vector: Any, source: str = "DREADNOUGHT"):
    """Globaler Einstiegspunkt für prozessinterne Morphismus-Pushes."""
    try:
        if isinstance(new_vector, list):
            new_vector = np.array(new_vector)
        # Sende via WebSocket an den laufenden Daemon auf 8001
        async with websockets.connect("ws://localhost:8001") as ws:
            await ws.send(json.dumps({
                "type": "PUSH_STATE",
                "category": category,
                "payload": new_vector.tolist(),
                "source": source
            }))
            logger.debug(f"[MORPHISM_PUSH] Gesendet an localhost:8001: {category}")
    except Exception as e:
        logger.error(f"[MORPHISM_PUSH] Fehler beim Senden an Daemon: {e}")

if __name__ == "__main__":
    morphism_stream = MorphismStream()
    try:
        asyncio.run(morphism_stream.run())
    except KeyboardInterrupt:
        logger.info("[MORPHISM] Server stopped.")
