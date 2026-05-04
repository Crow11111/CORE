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
MODEL_NAME = "gemini-3.1-pro-preview"

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
MASTERPLAN_PATH = DOCS_DIR / "05_AUDIT_PLANNING" / "MASTERPLAN_FTOE_V3_PRODUCER.md"
SOTA_PATH = DOCS_DIR / "05_AUDIT_PLANNING" / "SOTA_2026_WEB_RESEARCH_RESULTS.md"
OUTPUT_REPORTS = DOCS_DIR / "05_AUDIT_PLANNING" / "V3_INTERMEDIATE_REPORTS.md"
OUTPUT_V3 = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V3_Final.md"

# Load Masterplan and SOTA
def read_file(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

masterplan_content = read_file(MASTERPLAN_PATH)
sota_content = read_file(SOTA_PATH)

# Load old whitepapers for lost content
old_wp_files = [
    "01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md",
    "01_CORE_DNA/Whitepaper_V14_Final.md",
    "01_CORE_DNA/Whitepaper_V15_Lehrbuch.md",
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md"
]
old_wp_content = ""
for wp in old_wp_files:
    wp_path = DOCS_DIR / wp
    if wp_path.exists():
        with open(wp_path, "r", encoding="utf-8") as f:
            old_wp_content += f"\n\n--- {wp} ---\n{f.read()[:15000]}" # Limit size

# Load Deep Research Audits
dr_files = [
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_OMEGA PAPER.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_KAUSALITAET.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_speech.md"
]
dr_content = ""
for dr in dr_files:
    dr_path = DOCS_DIR / dr
    if dr_path.exists():
        with open(dr_path, "r", encoding="utf-8") as f:
            dr_content += f"\n\n--- {dr} ---\n{f.read()[:15000]}" # Limit size

print(f"Starte Producer Agent (Phase 1: Zwischenberichte) mit Modell {MODEL_NAME}...\n")

system_instruction_reports = r"""Du bist der OMEGA CORE Producer Agent. Deine Aufgabe ist die strikte Analyse, Verifikation und Falsifikation der Kritikpunkte an der FTOE V2.
Du schreibst ZWISCHENBERICHTE für die 4 Hauptkritikpunkte aus dem Masterplan.
Nutze die SOTA 2026 Ergebnisse, die alten Whitepapers und die DeepResearch-Audits, um die Kritikpunkte zu verifizieren oder zu falsifizieren.
Dein Output ist ein Markdown-Dokument mit den 4 detaillierten Zwischenberichten.
"""

prompt_reports = f"""
MASTERPLAN:
{masterplan_content}

SOTA 2026 ERGEBNISSE:
{sota_content}

ALTE WHITEPAPERS (Auszüge):
{old_wp_content}

DEEP RESEARCH AUDITS (Auszüge):
{dr_content}

AUFGABE:
Erstelle die 4 Zwischenberichte gemäß dem Masterplan. Analysiere jeden Kritikpunkt, verifiziere/falsifiziere ihn anhand der Daten und erkläre, wie er in V3 umgesetzt wird.
"""

try:
    response_reports = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_reports,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction_reports,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    reports_text = response_reports.text
    with open(OUTPUT_REPORTS, "w", encoding="utf-8") as f:
        f.write(reports_text)
    print(f"Zwischenberichte gespeichert unter: {OUTPUT_REPORTS}")
except Exception as e:
    print(f"Fehler bei der Generierung der Zwischenberichte: {e}")
    sys.exit(1)

print(f"\nStarte Producer Agent (Phase 2: V3 Whitepaper Erstellung)...\n")

system_instruction_v3 = r"""Du bist der OMEGA CORE Producer Agent. Deine finale Aufgabe ist die Erstellung des Whitepapers V3 (FTOE).
Du musst die Zwischenberichte, die SOTA-Ergebnisse und die Anweisungen aus dem Masterplan (6D-Raum, verlorene Inhalte wie 3-Körper-Problem) in ein stringentes, wissenschaftlich unangreifbares Whitepaper gießen.
Beachte zwingend das No-Drop-Protokoll: Keine Inhalte aus V2 dürfen verloren gehen, sie müssen nur gehärtet und erweitert werden.
"""

prompt_v3 = f"""
MASTERPLAN:
{masterplan_content}

ZWISCHENBERICHTE (Deine Analyse):
{reports_text}

SOTA 2026 ERGEBNISSE:
{sota_content}

AUFGABE:
Schreibe das vollständige, finale Whitepaper V3 ("FTOE_Theorie_der_latenten_Zeit_V3_Final.md").
Integriere alle Erkenntnisse aus den Zwischenberichten und der SOTA-Forschung.
Stelle den 6D-Raum klar heraus und bringe das 3-Körper-Problem und die Vorhersagen zurück.
"""

try:
    response_v3 = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_v3,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction_v3,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    v3_text = response_v3.text
    with open(OUTPUT_V3, "w", encoding="utf-8") as f:
        f.write(v3_text)
    print(f"V3 Whitepaper erfolgreich generiert und gespeichert unter: {OUTPUT_V3}")
except Exception as e:
    print(f"Fehler bei der Generierung von V3: {e}")
    sys.exit(1)
