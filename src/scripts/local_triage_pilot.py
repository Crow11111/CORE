# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
LOCAL TRIAGE PILOT (Split-Model Gemma 4 Edition).
Optimiert für RTX 3050 (8GB VRAM).
Level 1: gemma4:e2b (VRAM-resident)
Level 2: gemma4:e4b (Hybrid/Cloud Fallback)
"""

import os
import time
import json
import requests
from typing import Dict, Any
from loguru import logger
from dotenv import load_dotenv

load_dotenv("/OMEGA_CORE/.env")

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_LOCAL_HOST", "http://localhost:11434")
CORE_API_URL = os.getenv("CORE_API_URL", "http://localhost:8000")
MODEL_L1 = "gemma4:e2b"
MODEL_L2 = "gemma4:e4b"
LATENCY_THRESHOLD_S = 5.0

def get_active_mode() -> str:
    """Fragt den aktuellen Modus vom Backend ab."""
    try:
        r = requests.get(f"{CORE_API_URL}/api/v1/system/triage_mode", timeout=2)
        return r.json().get("mode", "NORMAL")
    except Exception as e:
        logger.warning(f"Konnte Modus nicht abrufen: {e}. Nutze NORMAL.")
        return "NORMAL"

def query_ollama_api(prompt: str, model: str) -> Dict[str, Any]:
    """Fragt die lokale Ollama API ab."""
    start_time = time.time()
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=45
        )
        response.raise_for_status()
        duration = time.time() - start_time
        result = response.json()
        return {
            "text": result.get("response", "").strip(),
            "duration": duration,
            "success": True
        }
    except Exception as e:
        logger.error(f"Ollama API Error ({model}): {e}")
        return {"text": "", "duration": time.time() - start_time, "success": False}

def triage_v3(message_text: str) -> str:
    """Gemma 4 Triage mit Modus-Bewusstsein."""
    mode = get_active_mode()
    logger.info(f"Aktiver Modus: {mode}")

    if mode == "NORMAL":
        return "NORMAL_CLOUD_ROUTING: Gemma 4 deaktiviert."

    # --- LEVEL 1: FAST SCOUT (gemma4:e2b) ---
    l1_prompt = f"""
    [TRIAGE L1] Klassifiziere die Nachricht:
    - SIMPLE: Ping, Hallo, Kurze Info
    - COMPLEX: Logik, Code, Architektur
    
    Antworte NUR mit dem Label.
    Nachricht: "{message_text}"
    """
    
    logger.info(f"[TAKT 1] Starte Level 1 Triage (Model: {MODEL_L1})")
    res_l1 = query_ollama_api(l1_prompt, MODEL_L1)
    
    if not res_l1["success"]:
        return "ERROR_L1_OLLAMA_OFFLINE"
    
    label = res_l1["text"].upper()
    logger.info(f"[TAKT 2] L1 Result: {label} ({res_l1['duration']:.2f}s)")
    
    if "SIMPLE" in label and mode != "MAXIMAL_LOKAL":
        return f"L1_PROCESSED: {label}"

    # --- LEVEL 2: DEEP TASK (gemma4:e4b / Cloud) ---
    if mode == "OPTIMAL":
        logger.info("[TAKT 3] OPTIMAL Modus: Delegiere Deep Task an Cloud (Gemini 3 Flash)")
        return "L2_CLOUD_DELEGATION"

    logger.info(f"[TAKT 3] Starte Level 2 Triage Lokal (Model: {MODEL_L2})")
    l2_prompt = f"""
    [TRIAGE L2] Analysiere detailliert:
    Nachricht: "{message_text}"
    Antworte mit JSON: {{"intent": "...", "complexity": "..."}}
    """
    
    res_l2 = query_ollama_api(l2_prompt, MODEL_L2)
    
    if res_l2["success"] and res_l2["duration"] < LATENCY_THRESHOLD_S:
        logger.info(f"[TAKT 4] L2 Result: {res_l2['text']} ({res_l2['duration']:.2f}s)")
        return f"L2_PROCESSED: {res_l2['text']}"
    else:
        logger.warning(f"[TAKT 4] L2 Slow ({res_l2['duration']:.2f}s) -> Fallback")
        return "L2_FALLBACK_REQUIRED"

if __name__ == "__main__":
    test_messages = ["@OC Ping", "Erkläre mir die 5D Kristall Topologie."]
    for msg in test_messages:
        print(f"\n--- Testing: {msg} ---")
        print(f"Result: {triage_v3(msg)}")
