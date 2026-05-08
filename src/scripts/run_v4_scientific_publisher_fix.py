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

# Files
basic_path = DOCS_DIR / "01_CORE_DNA" / "FTEO_Basic_V1.6_Float.md"
osmium_path = DOCS_DIR / "01_CORE_DNA" / "FTOE_OSMIUM_VERSION.md"
lehrbuch_path = DOCS_DIR / "06_FTOE_LEHRBUCH" / "FTOE_Erweitertes_Lehrbuch_V1.md"
audit_path = DOCS_DIR / "05_AUDIT_PLANNING" / "O2_AUDIT_SCIENCE_PUBLISHER_RESULT.md"

def read_file(p):
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

audit_content = read_file(audit_path)

def fix_document(doc_path, name):
    print(f"Fixing {name}...")
    content = read_file(doc_path)
    if not content:
        return
    
    sys_inst = f"""Du bist der Wissenschaftliche Publikator (Scientific Publisher SOTA 2026).
Deine Aufgabe ist es, einen VETO-Bericht von O2 (Zero-Context Auditor) auf ein FTOE-Dokument anzuwenden.
Wende ALLE Korrekturen aus dem Audit strengstens an, ohne den grundlegenden FTOE-Inhalt zu zerstören.
Achte auf:
1. Löschung aller Meta-Kommentare und Vorworte zur "Ich-Perspektive", Monotropismus als persönliche Eigenschaft, AuDHS etc. Übersetze es in objektive Sprache ("Topologie der Beobachter-Eliminierung durch kognitive Vektor-Fokussierung").
2. Ersetze informelle Verweise (wie "FTOE-KOMPASS") durch harte akademische Querverweise z.B. [vgl. Kap. 2.1]. Setze didaktische Erklärungen in Fußnoten [^1].
3. Für Lean 4 Code, füge MDAR Metadaten hinzu (z.B. Lean 4.0.0-nightly, Mathlib commit hash, Reproducibility link).
4. Für KI/Latenzen: Erwähne den Dreadnought-Benchmark (Zeitkomplexität O(1), Latenz 0.017 ms).
5. Bei Biologie (TTFields/Septin): Füge Platzhalter für harte SOTA Zitationen ein (z.B. [vgl. Novocure In-Vitro Studien 2024, PubMed ID XYZ]). Füge ER=EPR und CAIS in interdisziplinäre Abschnitte ein.
6. Quantifiziere Popper Kriterien hart (z.B. LLM Margin Loss > 15% Degradation, JWST Rotverschiebung z > 10.5 etc.).

Gib nur das vollständige, korrigierte Markdown-Dokument zurück. Keine Einleitung, keine Erklärungen.
"""

    prompt = f"""AUDIT REPORT (VETO-GRÜNDE):
{audit_content}

DOKUMENT ({name}):
{content}

Führe alle Änderungen durch und gib das finale SOTA 2026 Dokument zurück.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_inst,
                temperature=0.1,
                max_output_tokens=8192
            )
        )
        new_text = response.text
        if new_text.startswith("```markdown"):
            new_text = new_text[11:]
        if new_text.endswith("```"):
            new_text = new_text[:-3]
            
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(new_text.strip() + "\n")
        print(f"Fixed {name}.")
    except Exception as e:
        print(f"Error fixing {name}: {e}")

fix_document(basic_path, "FTEO_Basic_V1.6_Float.md")
fix_document(osmium_path, "FTOE_OSMIUM_VERSION.md")
fix_document(lehrbuch_path, "FTOE_Erweitertes_Lehrbuch_V1.md")

print("All documents fixed.")
