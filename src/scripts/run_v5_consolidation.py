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

# --- 1. Lade alle Dokumente ungedrosselt ---
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
total_chars = 0

print("Lese alle Dokumente ein (UNGEDROSSELT)...")
for f_path in all_files:
    full_path = DOCS_DIR / f_path
    if full_path.exists():
        content = read_file(full_path)
        all_content += f"\n\n{'='*50}\n--- DOKUMENT: {f_path} ---\n{'='*50}\n{content}"
        total_chars += len(content)
        print(f"  Gelesen: {f_path} ({len(content)} Zeichen)")
    else:
        print(f"  WARNUNG: {f_path} nicht gefunden.")

print(f"\nGesamte eingelesene Zeichen: {total_chars}")

# --- 2. Phase 1: Lehrbuch Konsolidierung ---
OUTPUT_LEHRBUCH = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V5_Lehrbuch_Consolidated.md"
OUTPUT_LEHRBUCH_PROPOSED = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V5_Lehrbuch_Proposed.md"

print("\nStarte Phase 1: Lehrbuch Konsolidierung...")
sys_inst_lehrbuch = """Du bist der OMEGA CORE Producer.
Deine Aufgabe ist die KONSOLIDIERUNG bestehender Whitepapers und Referenzdokumente zu EINER finalen Lehrbuch-Version.
DU DARFST NICHT FREI SCHREIBEN. Du musst die vorgegebenen Dokumente als Grundlage nehmen.

ZIEL: LEHRBUCH-VERSION
- Behalte die vorgefundene Struktur der Basis-Dokumente bei.
- Schlüssele es für alle Fachbereiche auf (nutze den Rosetta-Stein).
- Es MÜSSEN ALLE Punkte, Beispiele und Details aus ALLEN Basis- und Referenzdokumenten in erschöpfendem Umfang enthalten sein. KEIN Informationsverlust. Keine Zusammenfassungen, die Details weglassen.
- Integriere die Kritik aus `trasn.txt` (harte Falsifikation, keine Strohmann-Argumente, Prolog als roter Faden) als globale Anweisung für alle Kapitel.
- Integriere alle Deep Research Dokumente.

SONDERREGEL (VORSCHLÄGE):
Wenn du der Ansicht bist, dass die Dokumente anders strukturiert werden müssen oder Punkte/Beispiele überflüssig sind:
1. Setze dies NICHT in dieser Consolidated-Version um!
2. Schreibe deine Anmerkungen an das Ende der Consolidated-Datei.
"""

prompt_lehrbuch = f"""
ROHDATEN (ALLE DOKUMENTE):
{all_content}

Erstelle jetzt die `FTOE_Theorie_der_latenten_Zeit_V5_Lehrbuch_Consolidated.md`.
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
    with open(OUTPUT_LEHRBUCH, "w", encoding="utf-8") as f:
        f.write(response_lehrbuch.text)
    print(f"Lehrbuch erfolgreich generiert: {OUTPUT_LEHRBUCH}")
except Exception as e:
    print(f"Fehler in Phase 1: {e}")

# --- 3. Phase 2: Scientific Konsolidierung ---
OUTPUT_SCIENTIFIC = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V5_Scientific_Consolidated.md"
OUTPUT_SCIENTIFIC_PROPOSED = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V5_Scientific_Proposed.md"

print("\nStarte Phase 2: Scientific Konsolidierung...")
sys_inst_scientific = """Du bist der OMEGA CORE Producer.
Deine Aufgabe ist die KONSOLIDIERUNG bestehender Whitepapers und Referenzdokumente zu EINER finalen Scientific-Version.
DU DARFST NICHT FREI SCHREIBEN. Du musst die vorgegebenen Dokumente als Grundlage nehmen.

ZIEL: SCIENTIFIC-VERSION
- Inhaltlich müssen ALLE Punkte aus den Basis- und Referenzdokumenten enthalten sein.
- Zusammenfassungen sind hier erlaubt, ABER NUR ohne Informationsverlust.
- Setze die Kritik aus `trasn.txt` in absoluter Detailschärfe um (als globale Kritik für alle Kapitel).
- Integriere alle Deep Research Dokumente.

SONDERREGEL (VORSCHLÄGE):
Wenn du der Ansicht bist, dass die Dokumente anders strukturiert werden müssen oder Punkte/Beispiele überflüssig sind:
1. Setze dies NICHT in dieser Consolidated-Version um!
2. Schreibe deine Anmerkungen an das Ende der Consolidated-Datei.
"""

prompt_scientific = f"""
ROHDATEN (ALLE DOKUMENTE):
{all_content}

Erstelle jetzt die `FTOE_Theorie_der_latenten_Zeit_V5_Scientific_Consolidated.md`.
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
    with open(OUTPUT_SCIENTIFIC, "w", encoding="utf-8") as f:
        f.write(response_scientific.text)
    print(f"Scientific erfolgreich generiert: {OUTPUT_SCIENTIFIC}")
except Exception as e:
    print(f"Fehler in Phase 2: {e}")

print("\nAlle Phasen abgeschlossen.")
