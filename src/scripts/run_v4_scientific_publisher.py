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
OUTPUT_GAP = DOCS_DIR / "05_AUDIT_PLANNING" / "V4_GAP_ANALYSIS_AND_RESEARCH.md"
OUTPUT_V4 = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V4_Scientific.md"

def read_file(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 1. Load Scientific Publisher Skill
skill_path = BASE_DIR / ".cursor" / "skills" / "scientific-publisher" / "SKILL.md"
skill_content = read_file(skill_path)

# 2. Load all Deep Research and Core Documents (NO LIMITS)
files_to_read = [
    "05_AUDIT_PLANNING/MASTERPLAN_FTOE_V3_PRODUCER.md",
    "05_AUDIT_PLANNING/SOTA_2026_WEB_RESEARCH_RESULTS.md",
    "01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md",
    "01_CORE_DNA/Whitepaper_V14_Final.md",
    "01_CORE_DNA/Whitepaper_V15_Lehrbuch.md",
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md",
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V3_Final.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_OMEGA PAPER.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_KAUSALITAET.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_speech.md",
    "05_AUDIT_PLANNING/EMPIRICAL_NODE_COLLECTION.md",
    "05_AUDIT_PLANNING/DISSONANZ_SCHWELLWERTE_SPEC.md",
    "05_AUDIT_PLANNING/AGENT_WORKPACK_MESSBARE_ABNAHME_2026-04-05.md",
    "05_AUDIT_PLANNING/APOPTOSIS_FEP_RESULT.md",
    "05_AUDIT_PLANNING/COGNITIVE_UI_MANIFEST.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_KNOWLEDGE_INGEST_AUDIT.md",
    "05_AUDIT_PLANNING/RESULT_RESEARCH_V2.md"
]

all_content = ""
for f_path in files_to_read:
    full_path = DOCS_DIR / f_path
    if full_path.exists():
        content = read_file(full_path)
        all_content += f"\n\n{'='*50}\n--- DOKUMENT: {f_path} ---\n{'='*50}\n{content}"
    else:
        print(f"WARNUNG: {f_path} nicht gefunden.")

research_text = read_file(OUTPUT_GAP)

print("\nStarte Phase 2: Erstellung von FTOE V4 (Scientific Publisher)...")

sys_inst_v4 = f"""Du bist der Wissenschaftliche Publikator (Scientific Publisher SOTA 2026).
DEINE SKILL-DEFINITION:
{skill_content}

DEINE AUFGABE IN PHASE 2:
Schreibe das finale Whitepaper V4 ("FTOE_Theorie_der_latenten_Zeit_V4_Scientific.md").
Integriere ALLE Erkenntnisse aus deiner Gap-Analyse und den ungedrosselten Deep Research Dokumenten.
Setze die STAR und MDAR Richtlinien strikt um.
Füge ein massives Netz an Kreuzreferenzierungen (Cross-Referencing) und Fußnoten ein (z.B. [^1], [siehe Kap. 3]).
Härte jede Konstante und jedes Postulat mit SOTA 2026 Zitaten und Falsifizierbarkeitskriterien.
Achte darauf, dass die berechtigten Anmerkungen des O2 Audits (Relativitäts-Prüfung) respektiert werden: Klassische Werte (0.5, T=0, Q->0) dürfen zur Beschreibung des Problems oder klassischer Physik genannt werden, OMEGA-Zustände müssen die Axiome einhalten.
Das Dokument muss die absolute Speerspitze der wissenschaftlichen Publikation darstellen.
"""

prompt_v4 = f"""
GAP-ANALYSE & RESEARCH MASTERPLAN:
{research_text}

ROHDATEN (ALLE DOKUMENTE):
{all_content}

Schreibe jetzt das vollständige, wissenschaftlich rigorose Whitepaper V4.
"""

try:
    response_v4 = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_v4,
        config=types.GenerateContentConfig(
            system_instruction=sys_inst_v4,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    v4_text = response_v4.text
    with open(OUTPUT_V4, "w", encoding="utf-8") as f:
        f.write(v4_text)
    print(f"V4 Whitepaper erfolgreich generiert und gespeichert unter: {OUTPUT_V4}")
except Exception as e:
    print(f"Fehler in Phase 2: {e}")
    sys.exit(1)
