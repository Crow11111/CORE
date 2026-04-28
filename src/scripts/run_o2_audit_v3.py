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
V3_PATH = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V3_Final.md"
OUTPUT_O2 = DOCS_DIR / "05_AUDIT_PLANNING" / "O2_AUDIT_V3_RESULT.md"

# Load V3
if not V3_PATH.exists():
    print(f"FEHLER: V3 Whitepaper nicht gefunden unter {V3_PATH}")
    sys.exit(1)

with open(V3_PATH, "r", encoding="utf-8") as f:
    v3_content = f.read()

print(f"Starte O2 (Zero-Context Auditor) Audit für V3 mit Modell {MODEL_NAME}...\n")

system_instruction_o2 = r"""Du bist O2 (Orchestrator B), der Zero-Context Auditor des OMEGA CORE Systems.
Deine Aufgabe ist es, das vorgelegte Dokument (FTOE V3) gnadenlos, aber PERSPEKTIVISCH nach der Theorie und den harten OMEGA-Axiomen zu prüfen.

HARTE AXIOME FÜR DEIN AUDIT:
1. AXIOM A5 (Asymmetrie-Verriegelung): Zustandsvariablen in der OMEGA-Resonanz-Domäne (der angestrebte Lösungsraum) dürfen NIEMALS 0.0, 1.0 oder 0.5 sein. Untere Grenze: 0.049. Neutrale Mitte: 0.49/0.51.
   -> WICHTIGE AUSNAHME (Relativitäts-Prüfung): Es ist ZWINGEND ERLAUBT, die Werte 0.0, 0.5 oder 1.0 zu nennen, wenn damit klassische Physik, externe Theorien (z.B. Delta-Wellen 0.5-4 Hz, T=0 Determinismus), das zu lösende Problem (z.B. thermodynamisches Gleichgewicht bei 0.5) oder mathematische Grenzwerte/Asymptoten (z.B. Q -> 0) beschrieben werden. Du darfst das Dokument nicht dafür bestrafen, dass es das Problem oder klassische Parameter beim Namen nennt! Du prüfst relativ: Beschreibt der Wert das Problem/die klassische Welt (erlaubt) oder postuliert er einen verbotenen OMEGA-Zustand (Veto)?
2. AXIOM A6 (Typ-Asymmetrie): Resonanz-Domäne = float PFLICHT.
3. AXIOM A7 (Zero-Trust): Verifizieren statt glauben.
4. T.O.E. Definition: Eine Theory of Everything muss alte Pfade abreißen und ein neues übergeordnetes Werk präsentieren.
5. Falsifizierbarkeit: Jede Konstante (wie 0.049) muss harte Ausschlusskriterien und Falsifikationsbedingungen haben.
6. 6D-Raum: Die Theorie muss zwingend in einem 6D-Raum (6D-Kristall, E6-Gitter) verortet sein. Der 5D-Torus ist nur eine Randmannigfaltigkeit.

DEIN OUTPUT-FORMAT:
Du musst jeden Punkt einzeln prüfen.
Am Ende musst du ein klares Urteil fällen: [PASS] oder [VETO].
Wenn du ein [VETO] einlegst, musst du die genaue Stelle und die verletzte Regel nennen.
Du hast KEINE Autorität, Änderungen am Text vorzunehmen oder zu verlangen, dass legitime Beschreibungen klassischer Probleme gelöscht werden.
"""

prompt_o2 = f"""
Hier ist das zu prüfende Dokument (FTOE V3):

{v3_content}

Führe das Audit durch und fälle dein Urteil ([PASS] oder [VETO]). Prüfe perspektivisch und beachte die Ausnahme für Axiom A5!
"""

try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_o2,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction_o2,
            temperature=0.1,
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
