import requests
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

def run_o2_audit():
    logger.info("Starte O2 Zero-Context Audit via lokalem Ollama (gemma:2b für Speed)...")
    
    with open("src/scripts/o2_audit_theses.md", "r") as f:
        theses = f.read()
        
    prompt = f"""
Du bist O2, ein gnadenloser, blinder mathematischer und systemischer Auditor. 
Evaluiere die FTOE-Thesen streng gegen SOTA Mai 2026.
Wenn etwas Quatsch ist, nenne es Quatsch.

### Thesen:
{theses}

### SOTA 2026 Fakten:
1. Tensor Brain (2024-2026): Gehirn als Tensor-Netzwerk, Symbole/Embeddings auf "global workspace" (arXiv:2409.12846).
2. Quantum Convolutional Neural Networks (2026): Topologische Phasenübergänge identifizieren.
3. Operator-Algebren im Bewusstsein-Physik-Interface (2026).

### Beantworte streng:
1. Was ist nachgewiesener Quatsch?
2. Was hat logischen Halt (Tensor-Netzwerke, Operator-Algebren)?
3. Was ist metaphorischer Quatsch, hat aber einen brauchbaren SOTA-Kern (z.B. Tensorprodukte für Kognition)?
"""

    payload = {
        "model": "gemma:2b", # Kleines Modell für Speed
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        audit_output = result.get("response", "Kein Output")
        
        with open("docs/05_AUDIT_PLANNING/O2_AUDIT_SEMANTIK_HEX.md", "w") as f:
            f.write("# O2 ZERO-CONTEXT AUDIT: SEMANTISCHE TOPOLOGIE (Mai 2026)\n\n")
            f.write(audit_output)
            
        logger.info("Audit abgeschlossen.")
        print("=== O2 AUDIT RESULTAT ===")
        print(audit_output)
        
    except Exception as e:
        logger.error(f"Fehler bei O2 Ollama Audit: {e}")

if __name__ == "__main__":
    run_o2_audit()
