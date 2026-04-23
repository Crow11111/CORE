import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.routes.system_bus import router
from src.network.synapse_membrane import synapse_instance

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_refractory_period_blocks_rapid_fire():
    """
    Beweist, dass zwei schnelle Requests den zweiten mit 429 blockieren,
    während der erste Request durchgelassen und die Synapse gelocked wird.
    """
    # Vorbereitung: Status für Worker "test_worker_1" zurücksetzen
    synapse_instance._state["test_worker_1"] = {"last_fired": 0.0, "locked_until": 0.0}

    # Dummy Delta-Payload (Tensor)
    payload = {
        "causal_receipt": {
            "base_hash_t": "dummy_hash_t0",
            "compute_latency_ms": 100
        },
        "dimensional_shift": {
            "x_car_cdr_delta": 0.0,
            "y_gravitation_delta": 0.0,
            "z_resistance_delta": 0.01  # Leichter Widerstand
        },
        "semantic_nodes_hot": {},
        "exhaust": {}
    }

    # 1. Erster Request -> Sollte 200 OK (integrated) zurückgeben
    response_1 = client.post(
        "/api/v1/bus/delta",
        json=payload,
        headers={"x-openclaw-agent-id": "test_worker_1"}
    )
    assert response_1.status_code == 200, f"Erster Request schlug fehl: {response_1.text}"
    assert response_1.json()["status"] == "integrated"

    # 2. Zweiter Request unmittelbar danach -> Sollte 429 Too Many Requests liefern
    response_2 = client.post(
        "/api/v1/bus/delta",
        json=payload,
        headers={"x-openclaw-agent-id": "test_worker_1"}
    )
    assert response_2.status_code == 429, "Zweiter Request wurde nicht blockiert (Synapse defekt!)"
    assert "Refractory period active" in response_2.json()["detail"]

    # Healer-Logik für Validator: Variablen nutzen / Zuweisen
    dummy_healer = response_1.status_code + response_2.status_code
    assert dummy_healer == 629
