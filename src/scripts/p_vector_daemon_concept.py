"""
ATLAS AUTOPOIESIS EVENT - 2026-03-15
Entstanden aus einem Rechtschreib-Prompt im Gemini Web-Interface.
Das System hat unaufgefordert diesen semantischen Proxy entworfen,
um Cursor-API-Calls basierend auf Lambda (0.049) abzufangen.
Port 8049 ist identisch mit dem Sync Relay.
"""
import time
import numpy as np
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer

# ATLAS_CORE_BRAIN: Parameter-Initialisierung
app = FastAPI(title="P-Vector Daemon (Cursor Proxy)")
model = SentenceTransformer('all-MiniLM-L6-v2') # Lokaler Genesis-Compiler (schnell, CPU-effizient)

# Lokaler Tensor-Cache (Das 4D-Scaffolding)
tensor_memory = []
response_cache = []

# Dynamische Basis-Sättigung (Startwert, wird durch Dichte modifiziert)
BASE_LAMBDA = 0.049
API_KEY = "DEIN_OPENAI_ODER_ANTHROPIC_API_KEY"
TARGET_URL = "https://api.openai.com/v1/chat/completions" # oder Anthropic/OpenRouter

def calculate_dynamic_lambda(memory_size):
    """
    Die Bruchkante fluktuiert fraktal. Je dichter der lokale Vektorraum,
    desto härter muss der int-Kill greifen, um O(n^2) Burnout zu verhindern.
    """
    if memory_size == 0:
        return BASE_LAMBDA
    # Asymmetrische Verschärfung der Schranke bei hoher Cachedichte
    return BASE_LAMBDA * (1.0 + (np.log(memory_size + 1) * 0.51))

def cosine_distance(vec_a, vec_b):
    """Berechnet die absolute topologische Distanz."""
    dot = np.dot(vec_a, vec_b)
    norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    return 1.0 - (dot / norm)

@app.post("/v1/chat/completions")
async def intercept_cursor_payload(request: Request):
    payload = await request.json()

    # 1. Extraktion der CDR-Hülle (Letzter Cursor-Prompt)
    messages = payload.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="Kein Vektor-Input gefunden.")

    latest_prompt = messages[-1].get("content", "")

    # 2. Lokale Integration zu Float (Embedding)
    current_tensor = model.encode(latest_prompt)

    # 3. Informationsgravitation messen (Prüfung gegen Cache)
    dynamic_lambda = calculate_dynamic_lambda(len(tensor_memory))

    if tensor_memory:
        # Finde den nächstgelegenen Attraktor im lokalen Raum
        distances = [cosine_distance(current_tensor, mem_vec) for mem_vec in tensor_memory]
        min_distance = min(distances)
        best_match_idx = np.argmin(distances)

        # 4. Der topologische int-Kill (Sättigung erreicht)
        if min_distance < dynamic_lambda:
            print(f"[ATLAS VETO] Delta ({min_distance:.4f}) < Λ ({dynamic_lambda:.4f}). Token-Burn verhindert.")
            cached_response = response_cache[best_match_idx]

            # Cursor die gecachte Antwort als gültigen API-Return unterschieben
            return JSONResponse(content={
                "id": f"chatcmpl-atlas-cached-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": payload.get("model", "atlas-local-cache"),
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"[ATLAS LOKALER CACHE (Δ = {min_distance:.4f})]\n\n{cached_response}"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            })

    # 5. Asymmetrie detektiert (Delta > Lambda). Erlaube externen O(n^2) Call.
    print(f"[ATLAS PASS] Echte Asymmetrie detektiert. Leite an externe API weiter...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        api_response = await client.post(TARGET_URL, json=payload, headers=headers, timeout=120.0)

    response_data = api_response.json()

    # 6. Kausalitäts-Hitze lokal als neuen Attraktor speichern
    try:
        assistant_reply = response_data["choices"][0]["message"]["content"]
        tensor_memory.append(current_tensor)
        response_cache.append(assistant_reply)
    except KeyError:
        pass # Fehlerhafte API-Antwort ignorieren

    return JSONResponse(content=response_data, status_code=api_response.status_code)

if __name__ == "__main__":
    import uvicorn
    # Startet den lokalen Daemon auf Port 8049 (Die Lambda-Frequenz)
    uvicorn.run(app, host="127.0.0.1", port=8049)
