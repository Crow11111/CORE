import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

PLAN_PATH = Path("/OMEGA_CORE/docs/05_AUDIT_PLANNING/PLAN_OMEGA_HEX_COMPILER.md")
OUTPUT_PATH = Path("/OMEGA_CORE/docs/05_AUDIT_PLANNING/O2_AUDIT_HEX_COMPILER.md")

with open(PLAN_PATH, "r", encoding="utf-8") as f:
    plan_content = f.read()

system_instruction_o2 = r"""Du bist O2 (Orchestrator B), der Zero-Context Auditor des OMEGA CORE Systems.
Deine Aufgabe ist es, den vorgelegten Masterplan für den "Omega Hex-Compiler (Semantischer Faraday-Käfig)" gnadenlos nach der Theorie und den harten OMEGA-Axiomen zu prüfen.

HARTE AXIOME FÜR DEIN AUDIT:
1. AXIOM 7 (Zero-Trust): Verhindert dieser Plan wirklich, dass das LLM durch semantische Tricks (Prosa, Erklärungen) den Positiv-Positiv-Fall sabotiert?
2. Machbarkeit: Ist Variante C (LPIS-Vektor-Protokoll mit Vakuum-Apoptose) logisch schlüssig und mit aktuellen APIs (Gemini JSON-Mode) umsetzbar?
3. Lean 4 Integration: Ist Lean 4 korrekt als absoluter Gatekeeper (Ingress/Egress) positioniert? Darf das LLM Lean 4 umgehen? (Wenn ja -> VETO).

DEIN OUTPUT-FORMAT:
Führe eine kurze, harte Analyse durch.
Am Ende musst du ein klares Urteil fällen: [PASS] oder [VETO].
Wenn [PASS], gib eine kurze Empfehlung für die Umsetzung.
"""

prompt_o2 = f"""
Hier ist der zu prüfende Plan:

{plan_content}

Führe das Audit durch und fälle dein Urteil ([PASS] oder [VETO]).
"""

try:
    print("Frage echten O2 nach Audit für Hex-Compiler Plan...")
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_o2,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction_o2,
            temperature=0.1,
            max_output_tokens=8192
        )
    )
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"O2 Audit erfolgreich generiert: {OUTPUT_PATH}")
except Exception as e:
    print(f"Fehler beim O2 Audit: {e}")
    sys.exit(1)
