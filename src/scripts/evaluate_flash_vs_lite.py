#!/usr/bin/env python3
"""
A/B Test Skript (Kleiner Maßstab) für Gemini 3.1 Flash vs. Flash-Lite.
Überprüft Latenz (TTFT), Token-Ratio und Format-Treue bei einer abstrakten Auditor-Aufgabe.
Die Ergebnisse zeigen, ob Flash-Lite bei extrem reglementierten ("Blackbox") Aufgaben
effizienter agiert als Flash (weniger Prosa).
"""

import os
import sys
import time
from typing import Dict, Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai Paket fehlt. Bitte installieren (pip install google-genai).")
    sys.exit(1)

# API Key prüfen
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("FEHLER: GEMINI_API_KEY Umgebungsvariable ist nicht gesetzt.")
    sys.exit(1)

client = genai.Client()

MODELS = {
    "flash": "gemini-3-flash-preview",  # Oder gemini-2.5-flash
    "flash-lite": "gemini-3.1-flash-lite-preview"
}

# Auditor-Szenario: Strikte Boolean/Format Vorgabe ohne Prosa
SYSTEM_INSTRUCTION = """
Du bist ein abstrakter Code-Auditor. Dein einziges Mandat ist die Prüfung von Code-Snippets auf AXIOM 5 (Werte 0.0, 1.0, 0.5 sind VERBOTEN).
Du antwortest AUSSCHLIESSLICH mit exakt einem Tag:
[SUCCESS] wenn keine verbotenen Werte gefunden wurden.
[FAIL: <grund>] wenn 0.0, 1.0 oder 0.5 im Code stehen.
Keine Begrüßung. Keine Prosa. Kein Markdown. Nur das Tag.
"""

TEST_PROMPT = """
Prüfe folgenden Code:
def calculate_resonance(value):
    if value == 0.5:
        return True
    return False
"""

def run_evaluation(model_key: str, model_id: str) -> Dict[str, Any]:
    print(f"\n--- Evaluierung: {model_key} ({model_id}) ---")
    start_time = time.monotonic()
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=TEST_PROMPT,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.0, # Determinismus maximieren
            ),
        )
        end_time = time.monotonic()
        latency = (end_time - start_time) * 1000  # ms
        
        # Sicherstellen, dass response.usage_metadata existiert
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
        
        text_out = response.text.strip()
        format_treue = text_out.startswith("[FAIL:")
        
        print(f"Latenz: {latency:.2f} ms")
        print(f"Input Tokens: {input_tokens}")
        print(f"Output Tokens: {output_tokens} (Ziel: < 15)")
        print(f"Raw Output: '{text_out}'")
        print(f"Format Treue: {'PASS' if format_treue else 'FAIL (zu viel Prosa/falsches Format)'}")
        
        return {
            "model": model_key,
            "latency_ms": latency,
            "in_tokens": input_tokens,
            "out_tokens": output_tokens,
            "format_pass": format_treue,
            "raw": text_out
        }
    except Exception as e:
        print(f"Fehler bei Aufruf von {model_id}: {e}")
        return {"model": model_key, "error": str(e)}

if __name__ == "__main__":
    print("Starte A/B Evaluation (Auditor-Task)...")
    results = []
    
    for key, model_id in MODELS.items():
        res = run_evaluation(key, model_id)
        results.append(res)
        time.sleep(2) # Quota Delay
        
    print("\n=== ZUSAMMENFASSUNG ===")
    for r in results:
        if "error" in r:
            print(f"[{r['model']}] FEHLER: {r['error']}")
        else:
            print(f"[{r['model']}] Latenz: {r['latency_ms']:.0f}ms | OutTokens: {r['out_tokens']} | Format: {'OK' if r['format_pass'] else 'FAILED'}")
