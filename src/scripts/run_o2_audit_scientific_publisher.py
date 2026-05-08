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

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.1-pro-preview"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"

# Docs to check
doc_paths = [
    DOCS_DIR / "01_CORE_DNA" / "FTEO_Basic_V1.6_Float.md",
    DOCS_DIR / "01_CORE_DNA" / "FTOE_OSMIUM_VERSION.md",
    DOCS_DIR / "06_FTOE_LEHRBUCH" / "FTOE_Erweitertes_Lehrbuch_V1.md"
]

OUTPUT_O2 = DOCS_DIR / "05_AUDIT_PLANNING" / "O2_AUDIT_SCIENCE_PUBLISHER_RESULT.md"

def read_file(p):
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

skill_path = BASE_DIR / ".cursor" / "skills" / "scientific-publisher" / "SKILL.md"
skill_content = read_file(skill_path)

all_content = ""
for p in doc_paths:
    all_content += f"\n\n{'='*50}\n--- DOKUMENT: {p.name} ---\n{'='*50}\n"
    all_content += read_file(p)

print(f"Starte O2 (Scientific Publisher Auditor) Audit mit Modell {MODEL_NAME}...\n")

system_instruction_o2 = f"""Du bist O2 (Orchestrator B), der Zero-Context Auditor des OMEGA CORE Systems.
Gleichzeitig wendest du den SKILL 'Wissenschaftlicher Publikator (Scientific Publisher SOTA 2026)' an.

DEINE SKILL-DEFINITION (Scientific Publisher):
{skill_content}

HARTE AXIOME FÜR DEIN AUDIT:
1. STAR & MDAR Richtlinien: Sind Methodik, Parameter und Benchmarks klar benannt?
2. Kreuzreferenzierung (Cross-Referencing): Sind interne Querverweise konsistent und logisch?
3. SOTA-Kontextualisierung: Hält die Theorie dem Vergleich mit der Speerspitze der Wissenschaft 2026 stand?
4. Falsifizierbarkeit: Sind harte Ausschlusskriterien (Popper) definiert?
5. Zero-Trust: Keine Metakommentare oder Relativierungen im Dokument.

DEIN OUTPUT-FORMAT:
Du musst eine tiefgreifende inhaltliche und methodische Analyse durchführen. 
Prüfe die drei FTOE-Dokumente (Basic, Osmium, Lehrbuch) auf Einhaltung der Publikationsstandards und der OMEGA-Axiome.
Finde Lücken in der Beweisführung, fehlerhafte Kreuzreferenzen oder fehlende SOTA-Einbettung.
Gib am Ende ein klares Urteil ab: [PASS] oder [VETO].
Bei [VETO] nenne zwingend die exakten Mängel und fordere konkrete Änderungen an den Texten.
"""

prompt_o2 = f"""
Hier sind die zu prüfenden Dokumente (FTOE Master Suite):

{all_content}

Führe das rigorose Scientific Publisher Audit durch. 
Sind die Dokumente reif für eine SOTA 2026 Publikation in Top-Tier Journals?
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
        print("\nERGEBNIS: UNKLAR")

except Exception as e:
    print(f"Fehler beim O2 Audit: {e}")
    sys.exit(1)
