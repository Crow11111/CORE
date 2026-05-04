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

def read_file(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

basis_files = [
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V4_Scientific draft.md",
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md",
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md",
    "01_CORE_DNA/Theorie_der_latenten_Zeit_V1.1_Lehrbuch_Draft.md",
    "01_CORE_DNA/Whitepaper_V15_Lehrbuch.md",
    "01_CORE_DNA/Whitepaper_V14_Final.md"
]

referenz_files = [
    "01_CORE_DNA/03_TOPOLOGISCHE_MATRIX.md",
    "01_CORE_DNA/04_THEORIE_DER_0_UND_1.md",
    "01_CORE_DNA/05_TOPOLOGISCHE_MEDIEN_REGULATION.md",
    "01_CORE_DNA/5D_TORUS_KRISTALL_ENGINE.md",
    "01_CORE_DNA/06_GEGEN_TENSORFELD_EMOTION_ZEIT.md",
    "01_CORE_DNA/07_SOZIOLOGIE_LPIS_MAPPING.md",
    "01_CORE_DNA/08_THEORY_OF_EMOTION.md",
    "01_CORE_DNA/09_ROSETTA_STEIN_DER_DISZIPLINEN.md"
]

kritik_files = [
    "01_CORE_DNA/trasn.txt",
    "05_AUDIT_PLANNING/EMPIRICAL_NODE_COLLECTION.md",
    "05_AUDIT_PLANNING/DISSONANZ_SCHWELLWERTE_SPEC.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_speech.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_OMEGA PAPER.md",
    "05_AUDIT_PLANNING/AGENT_WORKPACK_MESSBARE_ABNAHME_2026-04-05.md",
    "05_AUDIT_PLANNING/APOPTOSIS_FEP_RESULT.md",
    "05_AUDIT_PLANNING/COGNITIVE_UI_MANIFEST.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_KNOWLEDGE_INGEST_AUDIT.md",
    "05_AUDIT_PLANNING/RESULT_RESEARCH_V2.md"
]

all_files = basis_files + referenz_files + kritik_files
all_content = ""
for f_path in all_files:
    full_path = DOCS_DIR / f_path
    if full_path.exists():
        content = read_file(full_path)
        all_content += f"\n\n{'='*50}\n--- DOKUMENT: {f_path} ---\n{'='*50}\n{content}"

# Define the chapters we want to extract/consolidate
chapters = [
    "1. PROLOG & EPISTEMOLOGISCHE FUNDIERUNG (inkl. Neurodivergenz, Q-Variable)",
    "2. ARCHITEKTUR DES 6D-RAUMS & 5D-TORUS (inkl. Topologische Matrix, E6-Gitter)",
    "3. MATHEMATIK, GRENZWERTE & FALSIFIZIERBARKEIT (inkl. 0.049, Mitose-Algebra, Theorie der 0 und 1)",
    "4. PHYSIK & KOSMOLOGIE (inkl. Gegen-Tensorfeld, Zeit als Latenz, 3-Körper-Problem)",
    "5. KÜNSTLICHE INTELLIGENZ & INFORMATIK (inkl. LLM-Kollaps, Batch-Invariant Kernels, TDA)",
    "6. BIOLOGIE & CHEMIE (inkl. Apoptose, Proteinfaltung, LLPS)",
    "7. SOZIOLOGIE & KOGNITIVE UI (inkl. LPIS-Mapping, Medien-Regulation, LLI Prosthetic Gating)",
    "8. VORHERSAGEN, BEWEISE & EMPIRISCHE KNOTEN (inkl. Mendelejew-Schatten, Millersche Zahl)"
]

OUTPUT_LEHRBUCH = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V5_Lehrbuch_Consolidated.md"
OUTPUT_SCIENTIFIC = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V5_Scientific_Consolidated.md"

# Clear output files
open(OUTPUT_LEHRBUCH, "w").close()
open(OUTPUT_SCIENTIFIC, "w").close()

print("Starte Chunked Konsolidierung...")

for i, chapter in enumerate(chapters):
    print(f"\nVerarbeite Kapitel {i+1}/{len(chapters)}: {chapter}")
    
    # LEHRBUCH
    sys_inst_lehrbuch = f"""Du bist der OMEGA CORE Producer.
Deine Aufgabe ist die KONSOLIDIERUNG bestehender Whitepapers und Referenzdokumente für ein spezifisches Kapitel der LEHRBUCH-Version.
DU DARFST NICHT FREI SCHREIBEN. Du musst die vorgegebenen Dokumente als Grundlage nehmen.

ZIEL: KAPITEL "{chapter}" FÜR DIE LEHRBUCH-VERSION
- Extrahiere ALLE relevanten Informationen, Punkte, Beispiele und Details aus den Rohdaten, die zu diesem Thema passen.
- Schlüssele es verständlich auf (nutze den Rosetta-Stein).
- Es MÜSSEN ALLE Details in erschöpfendem Umfang enthalten sein. KEIN Informationsverlust.
- Integriere die Kritik aus `trasn.txt` (harte Falsifikation, keine Strohmann-Argumente, Prolog als roter Faden).
- Schreibe NUR dieses eine Kapitel.
"""
    
    prompt_lehrbuch = f"""
ROHDATEN (ALLE DOKUMENTE):
{all_content}

Erstelle jetzt das Kapitel "{chapter}" für die Lehrbuch-Version.
Verliere kein einziges Beispiel, keine Formel und keinen Absatz aus den Rohdaten, die zu diesem Thema gehören.
"""
    
    try:
        response_lehrbuch = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_lehrbuch,
            config=types.GenerateContentConfig(
                system_instruction=sys_inst_lehrbuch,
                temperature=0.1,
                max_output_tokens=8192
            )
        )
        with open(OUTPUT_LEHRBUCH, "a", encoding="utf-8") as f:
            f.write(f"\n\n## {chapter}\n\n" + response_lehrbuch.text)
        print(f"  -> Lehrbuch-Kapitel gespeichert.")
    except Exception as e:
        print(f"  -> Fehler in Lehrbuch-Kapitel: {e}")

    # SCIENTIFIC
    sys_inst_scientific = f"""Du bist der OMEGA CORE Producer.
Deine Aufgabe ist die KONSOLIDIERUNG bestehender Whitepapers und Referenzdokumente für ein spezifisches Kapitel der SCIENTIFIC-Version.
DU DARFST NICHT FREI SCHREIBEN. Du musst die vorgegebenen Dokumente als Grundlage nehmen.

ZIEL: KAPITEL "{chapter}" FÜR DIE SCIENTIFIC-VERSION
- Extrahiere ALLE relevanten harten Fakten, Formeln und SOTA-Referenzen aus den Rohdaten, die zu diesem Thema passen.
- Zusammenfassungen sind hier erlaubt, ABER NUR ohne Informationsverlust.
- Setze die Kritik aus `trasn.txt` in absoluter Detailschärfe um.
- Schreibe NUR dieses eine Kapitel.
"""
    
    prompt_scientific = f"""
ROHDATEN (ALLE DOKUMENTE):
{all_content}

Erstelle jetzt das Kapitel "{chapter}" für die Scientific-Version.
Führe alle harten Fakten, Formeln und SOTA-Referenzen zusammen, ohne etwas wegzulassen.
"""
    
    try:
        response_scientific = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_scientific,
            config=types.GenerateContentConfig(
                system_instruction=sys_inst_scientific,
                temperature=0.1,
                max_output_tokens=8192
            )
        )
        with open(OUTPUT_SCIENTIFIC, "a", encoding="utf-8") as f:
            f.write(f"\n\n## {chapter}\n\n" + response_scientific.text)
        print(f"  -> Scientific-Kapitel gespeichert.")
    except Exception as e:
        print(f"  -> Fehler in Scientific-Kapitel: {e}")

print("\nKonsolidierung abgeschlossen.")
