import asyncio
import unittest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from src.network.openclaw_client import OpenClawClient

class TestOpenClawBusSync(unittest.IsolatedAsyncioTestCase):
    """
    Testet die Kausalitätskette:
    1. Nachricht an OpenClaw senden.
    2. OpenClaw antwortet mit einem JSON-Delta (Tensor).
    3. OpenClawClient erkennt das Delta und injiziert es automatisch in den Systembus.
    4. Der Systembus antwortet mit einem neuen state_hash.
    """
    
    async def test_openclaw_bus_sync_chain(self):
        # Setup
        client = OpenClawClient(
            vps_host="localhost", 
            token="test-token", 
            backend_url="http://localhost:8000"
        )
        
        # Mock-Daten für das kognitive Delta
        mock_delta = {
            "causal_receipt": {
                "base_hash_t": "old-hash-123",
                "compute_latency_ms": 150
            },
            "dimensional_shift": {
                "x_car_cdr_delta": 0.05,
                "y_gravitation_delta": -0.1,
                "z_resistance_delta": 0.01
            },
            "semantic_nodes_hot": {"vps_config": 0.9},
            "exhaust": {"narrative_log": "Test integration successful"}
        }
        
        # Mock-Antwort vom OpenClaw Gateway
        mock_oc_response = {
            "output": [
                {
                    "type": "output_text",
                    "text": f"Simulation abgeschlossen. Delta: {json.dumps(mock_delta)}"
                }
            ]
        }
        
        # Mock-Antwort vom Systembus
        mock_bus_response = {
            "new_state_hash": "causal-hash-t-plus-1"
        }

        # Wir patchen httpx.AsyncClient.post um externe Requests zu simulieren
        with patch("httpx.AsyncClient.post") as mock_post:
            # Konfiguration der Side-Effects für die zwei erwarteten POST-Requests
            mock_post.side_effect = [
                AsyncMock(
                    status_code=200, 
                    json=lambda: mock_oc_response, 
                    raise_for_status=MagicMock()
                ),
                AsyncMock(
                    status_code=200, 
                    json=lambda: mock_bus_response, 
                    raise_for_status=MagicMock()
                )
            ]
            
            # Execution: Sende Nachricht an den Agenten
            success, response = await client.send_message_to_agent_async("Triggering sync...")
            
            # Verifikation
            self.assertTrue(success)
            self.assertIn("Simulation abgeschlossen", response)
            
            # Prüfen ob der neue state_hash im Client gesetzt wurde
            self.assertEqual(client.current_state_hash, "causal-hash-t-plus-1")
            
            # Prüfen der API-Aufrufe
            self.assertEqual(mock_post.call_count, 2)
            
            # Details des Bus-Pushes prüfen
            bus_call_args = mock_post.call_args_list[1]
            sent_json = bus_call_args.kwargs["json"]
            self.assertEqual(sent_json["causal_receipt"]["base_hash_t"], "old-hash-123")
            self.assertEqual(sent_json["dimensional_shift"]["x_car_cdr_delta"], 0.05)

if __name__ == "__main__":
    unittest.main()
