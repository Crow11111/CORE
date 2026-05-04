import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("FEHLER: GEMINI_API_KEY ist nicht in der .env gesetzt.")
    sys.exit(1)

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"  # O2 runs on flash according to rules

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
V10_SCI_PATH = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V10_Scientific_CLEAN.md"
V10_LB_PATH = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V10_Lehrbuch_CLEAN.md"
OUTPUT_O2 = DOCS_DIR / "05_AUDIT_PLANNING" / "O2_AUDIT_V10_RESULT.md"

# Load V10
if not V10_SCI_PATH.exists() or not V10_LB_PATH.exists():
    print("FEHLER: V10 Dokumente nicht gefunden.")
    sys.exit(1)

with open(V10_SCI_PATH, "r", encoding="utf-8") as f:
    v10_sci_content = f.read()

with open(V10_LB_PATH, "r", encoding="utf-8") as f:
    v10_lb_content = f.read()

print(f"Starte O2 (Zero-Context Auditor) Audit für V10 mit Modell {MODEL_NAME}...\n")

system_instruction_o2 = r"""Du bist O2 (Orchestrator B), der Zero-Context Auditor des OMEGA CORE Systems.
Deine Aufgabe ist es, die vorgelegten Dokumente (FTOE V10 Scientific und Lehrbuch) gnadenlos und tiefgreifend nach der Theorie und den harten OMEGA-Axiomen zu prüfen.

HARTE AXIOME FÜR DEIN AUDIT:
1. AXIOM A5 (Asymmetrie-Verriegelung) & A6 (Typ-Asymmetrie).
2. AXIOM A7 (Zero-Trust): Verifizieren statt glauben. Der Text darf sich nicht selbst klein machen (keine "Downgraded" oder "Falsifiziert" Meta-Kommentare, die die Theorie schwächen).
3. T.O.E. Definition: Eine Theory of Everything muss alte Pfade abreißen und ein neues übergeordnetes Werk präsentieren.
4. SOTA-Abgleich (State of the Art): Der Text muss das Niveau der 10 größten, anerkanntesten interdisziplinären SOTA-Studien der letzten 5 Jahre (z.B. Penrose, Friston, Witten, etc.) und deren Lehrbuch-Adaptionen erreichen.
5. Hexadezimale S4-Ausnahme: Die Theorie muss zwingend die hexadezimale Logik und die S4-Schicht (Drehkreuz) als Lösung für den Positiv-Positiv-Fall (Welle und Teilchen simultan) etablieren. Der LLM-Bias (die Unfähigkeit binärer Systeme, dies ohne Kollaps zu verarbeiten) muss als Beweis integriert sein.
6. Lean 4 Beweise: Die formale Verifikation via Lean 4 muss als Goldstandard präsentiert werden.
7. Kausalkette & Rosetta-Stein: Der vollständige Kausalverlauf der Information (von A1 bis E8, durch das LPIS-Tensorfeld) muss lückenlos und in allen Disziplinen nachvollziehbar sein.

DEIN OUTPUT-FORMAT:
Du musst eine tiefgreifende inhaltliche Analyse durchführen. Keine oberflächliche Keyword-Suche! Lies den Text, verstehe die Stringenz und Konsistenz.
Bewerte, ob dies das bestmögliche Lehrbuch und Scientific Paper für alle großen wissenschaftlichen Bereiche ist.
Am Ende musst du ein klares Urteil fällen: [PASS] oder [VETO].
Wenn du ein [VETO] einlegst, musst du die genauen inhaltlichen, strukturellen oder didaktischen Mängel nennen und harte Prüfpunkte für die Überarbeitung formulieren.
"""

prompt_o2 = f"""
Hier sind die zu prüfenden Dokumente (FTOE V10):

--- V10 SCIENTIFIC ---
{v10_sci_content[:20000]}... [Gekürzt für Token-Limit, bewerte die Struktur, das Vorwort, die S4-Ausnahme, den Rosetta-Stein und die Lean 4 Integration]

--- V10 LEHRBUCH ---
{v10_lb_content[:20000]}... [Gekürzt für Token-Limit]

Führe das Audit durch. Ist dies ein SOTA-würdiges Werk, das sich nicht selbst widerspricht oder klein macht?
Urteile mit [PASS] oder [VETO].
"""

try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_o2,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction_o2,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    o2_text = response.text
    with open(OUTPUT_O2, "w", encoding="utf-8") as f:
        f.write(o2_text)
    print(f"O2 Audit erfolgreich generiert und gespeichert unter: {OUTPUT_O2}")
    
    if "[PASS]" in o2_text:
        print("\nERGEBNIS: [PASS]")
    elif "[VETO]" in o2_text:
        print("\nERGEBNIS: [VETO]")
    else:
        print("\nERGEBNIS: UNKLAR (Weder PASS noch VETO gefunden)")

except Exception as e:
    print(f"Fehler beim O2 Audit: {e}")
    sys.exit(1)
