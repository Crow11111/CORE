# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
LOCAL TRIAGE PILOT (Split-Model Edition).
Optimiert für RTX 3050 (8GB VRAM).
Level 1: gemma2:2b (VRAM-resident)
Level 2: gemma2:9b (Hybrid/Cloud Fallback)
"""

import os
import time
import json
import requests
import logging
from typing import Dict, Any

# Loguru Setup
from loguru import logger

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_L1 = "gemma2:2b"
MODEL_L2 = "gemma2:9b" # Q4_K_M recommended
LATENCY_THRESHOLD_S = 5.0

def query_ollama_api(prompt: str, model: str) -> Dict[str, Any]:
    """Fragt die lokale Ollama API ab (effizienter als Subprocess)."""
    start_time = time.time()
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_gpu": 43, # Force all layers if possible
                    "temperature": 0.0
                }
            },
            timeout=30
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

def triage_v2(message_text: str) -> str:
    """Zweistufige Triage: Level 1 lokal, Level 2 Hybrid/Cloud."""
    
    # --- LEVEL 1: FAST SCOUT (2b) ---
    l1_prompt = f"""
    [TRIAGE L1] Klassifiziere die Nachricht:
    - SIMPLE: Ping, Hallo, Kurze Info (< 5 Wörter)
    - COMPLEX: Logik, Code, Lange Fragen, Architektur
    
    Antworte NUR mit dem Label.
    Nachricht: "{message_text}"
    """
    
    logger.info(f"[TAKT 1] Starte Level 1 Triage (Model: {MODEL_L1})")
    res_l1 = query_ollama_api(l1_prompt, MODEL_L1)
    
    if not res_l1["success"]:
        return "ERROR_L1"
    
    label = res_l1["text"].upper()
    logger.info(f"[TAKT 2] L1 Result: {label} ({res_l1['duration']:.2f}s)")
    
    if "SIMPLE" in label:
        return f"L1_PROCESSED: {label}"

    # --- LEVEL 2: DEEP TASK (9b / Cloud) ---
    logger.info(f"[TAKT 3] Starte Level 2 Triage (Model: {MODEL_L2})")
    l2_prompt = f"""
    [TRIAGE L2] Analysiere detailliert:
    Nachricht: "{message_text}"
    
    Antworte mit JSON: {{"intent": "...", "complexity": "...", "target": "..."}}
    """
    
    res_l2 = query_ollama_api(l2_prompt, MODEL_L2)
    
    if res_l2["success"] and res_l2["duration"] < LATENCY_THRESHOLD_S:
        logger.info(f"[TAKT 4] L2 Result: {res_l2['text']} ({res_l2['duration']:.2f}s)")
        return f"L2_PROCESSED: {res_l2['text']}"
    else:
        logger.warning(f"[TAKT 4] L2 Timeout/Slow ({res_l2['duration']:.2f}s) -> CLOUD FALLBACK TRIGGERED")
        return "L2_CLOUD_FALLBACK"

if __name__ == "__main__":
    test_messages = [
        "@OC Ping",
        "Schreibe ein Python Skript das die Fibonacci Folge bis 100 berechnet und die Ergebnisse in eine CSV schreibt."
    ]
    
    for msg in test_messages:
        print(f"\n--- Testing: {msg} ---")
        print(f"Result: {triage_v2(msg)}")
