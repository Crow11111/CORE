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
OUTPUT_GAP = DOCS_DIR / "05_AUDIT_PLANNING" / "V4_DUAL_GAP_ANALYSIS.md"
OUTPUT_SCIENTIFIC = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V4_Scientific.md"
OUTPUT_LEHRBUCH = DOCS_DIR / "01_CORE_DNA" / "Theorie_der_latenten_Zeit_V1.2_Lehrbuch.md"

def read_file(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

skill_path = BASE_DIR / ".cursor" / "skills" / "scientific-publisher" / "SKILL.md"
skill_content = read_file(skill_path)

core_dna_files = [
    "01_CORE_DNA/03_TOPOLOGISCHE_MATRIX.md",
    "01_CORE_DNA/04_THEORIE_DER_0_UND_1.md",
    "01_CORE_DNA/05_TOPOLOGISCHE_MEDIEN_REGULATION.md",
    "01_CORE_DNA/5D_TORUS_KRISTALL_ENGINE.md",
    "01_CORE_DNA/06_GEGEN_TENSORFELD_EMOTION_ZEIT.md",
    "01_CORE_DNA/07_SOZIOLOGIE_LPIS_MAPPING.md",
    "01_CORE_DNA/08_THEORY_OF_EMOTION.md",
    "01_CORE_DNA/09_ROSETTA_STEIN_DER_DISZIPLINEN.md",
    "01_CORE_DNA/trasn.txt",
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V1_Final.md",
    "01_CORE_DNA/FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md",
    "01_CORE_DNA/Theorie_der_latenten_Zeit_V1.1_Lehrbuch_Draft.md",
    "01_CORE_DNA/Whitepaper_V15_Lehrbuch.md",
    "01_CORE_DNA/Whitepaper_V14_Final.md"
]

audit_files = [
    "05_AUDIT_PLANNING/MASTERPLAN_FTOE_V3_PRODUCER.md",
    "05_AUDIT_PLANNING/SOTA_2026_WEB_RESEARCH_RESULTS.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_OMEGA PAPER.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_KAUSALITAET.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_speech.md",
    "05_AUDIT_PLANNING/EMPIRICAL_NODE_COLLECTION.md",
    "05_AUDIT_PLANNING/DISSONANZ_SCHWELLWERTE_SPEC.md",
    "05_AUDIT_PLANNING/AGENT_WORKPACK_MESSBARE_ABNAHME_2026-04-05.md",
    "05_AUDIT_PLANNING/APOPTOSIS_FEP_RESULT.md",
    "05_AUDIT_PLANNING/COGNITIVE_UI_MANIFEST.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_KNOWLEDGE_INGEST_AUDIT.md",
    "05_AUDIT_PLANNING/RESULT_RESEARCH_V2.md",
    "05_AUDIT_PLANNING/O2_AUDIT_V3_RESULT.md"
]

all_files = core_dna_files + audit_files
all_content = ""
total_chars = 0

print("Lese Dateien ein (UNGEDROSSELT)...")
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

# PHASE 1: GAP ANALYSIS & DEEP RESEARCH
print("\nStarte Phase 1: Gap-Analyse & Deep Research (Scientific Publisher)...")
sys_inst_research = f"""Du bist der Wissenschaftliche Publikator (Scientific Publisher SOTA 2026).
DEINE SKILL-DEFINITION:
{skill_content}

DEINE AUFGABE IN PHASE 1:
1. Lies ALLE übergebenen Dokumente VOLLSTÄNDIG.
2. Führe eine ausführliche Deep Research Analyse durch: Identifiziere alle Probleme, Quellen, Zahlen und Postulate aus den Deep Research Dokumenten und den alten Whitepapern, die bisher verloren gingen.
3. Falsifiziere bzw. verifiziere diese Fakten gemäß deinem SOTA 2026 Wissen. Härte die Fakten.
4. Analysiere das Transkript (`trasn.txt`) als GLOBALE Kritik:
   - Harte Falsifikationsbedingungen für 0.049 (Abweichungen, Bärtierchen).
   - Keine Strohmann-Argumente (Levinthal), sondern Angriff auf SOTA-Theorien (Energy Landscape Theory, DFT, LQG/Stringtheorie).
   - Kognitive Besonderheit (Prolog) muss als durchgängiges methodologisches Beweisstück genutzt werden (Delta-Wellen, Q=S).
5. Erstelle einen Masterplan für ZWEI Dokumente:
   A) Die Fachpublikation (Scientific): Absolute Detailschärfe, SOTA-Angriffe, harte Falsifikation.
   B) Die Lehrbuchausgabe (General Audience): Erschöpfender Umfang, alle Beispiele, Nutzung des Rosetta-Steins (`09_ROSETTA_STEIN_DER_DISZIPLINEN.md`) für alle Fachbereiche.
"""

prompt_research = f"""
HIER SIND ALLE DOKUMENTE (UNGEDROSSELT):
{all_content}

Führe jetzt die Deep Research Gap-Analyse durch und erstelle den Dual-Publikations-Masterplan.
"""

try:
    response_research = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_research,
        config=types.GenerateContentConfig(
            system_instruction=sys_inst_research,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    research_text = response_research.text
    with open(OUTPUT_GAP, "w", encoding="utf-8") as f:
        f.write(research_text)
    print(f"Gap-Analyse & Research gespeichert unter: {OUTPUT_GAP}")
except Exception as e:
    print(f"Fehler in Phase 1: {e}")
    sys.exit(1)

# PHASE 2: SCIENTIFIC PUBLICATION
print("\nStarte Phase 2: Erstellung der Fachpublikation (Scientific)...")
sys_inst_scientific = f"""Du bist der Wissenschaftliche Publikator (Scientific Publisher SOTA 2026).
DEINE AUFGABE IN PHASE 2:
Schreibe das finale Whitepaper V4 ("FTOE_Theorie_der_latenten_Zeit_V4_Scientific.md") REIN FÜR DAS FACHPUBLIKUM.
- Setze die Kritik aus `trasn.txt` in ABSOLUTER Detailschärfe um.
- Härte jede Konstante mit SOTA 2026 Zitaten und Falsifizierbarkeitskriterien.
- Dekonstruiere aktuelle Theorien (Energy Landscape Theory, DFT, LQG) statt Strohmänner.
- Verknüpfe den Prolog (Neurodivergenz) methodisch mit den mathematischen Formeln.
- Das Dokument MUSS SEHR UMFANGREICH sein. Verliere keine harten Fakten aus den Deep Research Dokumenten.
- Beachte die berechtigten Anmerkungen des O2 Audits (Relativitäts-Prüfung erlaubt klassische Werte zur Problembeschreibung).
"""

prompt_scientific = f"""
GAP-ANALYSE & RESEARCH MASTERPLAN:
{research_text}

ROHDATEN (ALLE DOKUMENTE):
{all_content}

Schreibe jetzt die vollständige, wissenschaftlich rigorose Fachpublikation V4.
"""

try:
    response_scientific = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_scientific,
        config=types.GenerateContentConfig(
            system_instruction=sys_inst_scientific,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    with open(OUTPUT_SCIENTIFIC, "w", encoding="utf-8") as f:
        f.write(response_scientific.text)
    print(f"Fachpublikation erfolgreich generiert: {OUTPUT_SCIENTIFIC}")
except Exception as e:
    print(f"Fehler in Phase 2: {e}")

# PHASE 3: LEHRBUCH AUSGABE
print("\nStarte Phase 3: Erstellung der Lehrbuchausgabe...")
sys_inst_lehrbuch = f"""Du bist der Wissenschaftliche Publikator und Didaktiker des OMEGA CORE.
DEINE AUFGABE IN PHASE 3:
Schreibe die "Theorie_der_latenten_Zeit_V1.2_Lehrbuch.md" FÜR DIE ALLGEMEINHEIT.
- Nutze zwingend den Ansatz aus `09_ROSETTA_STEIN_DER_DISZIPLINEN.md`, um jeden Fachbereich in seiner Sprache, aber verständlich abzuholen.
- Das Dokument muss in ERSCHÖPFENDEM Umfang alle Punkte und Beispiele aus den alten Whitepapern (V14, V15) und den Deep Research Dateien enthalten.
- Erkläre die komplexe Mathematik und Physik durch anschauliche Metaphern und die gesammelten empirischen Knoten.
- Die globale Kritik aus `trasn.txt` muss stilistisch und didaktisch umgesetzt werden (z.B. klare Falsifizierbarkeit an Beispielen wie Bärtierchen erklären, den Prolog als roten Faden durch das Buch ziehen).
- Verliere keine Informationen, sondern mache sie zugänglich.
"""

prompt_lehrbuch = f"""
GAP-ANALYSE & RESEARCH MASTERPLAN:
{research_text}

ROHDATEN (ALLE DOKUMENTE):
{all_content}

Schreibe jetzt die vollständige, erschöpfende Lehrbuchausgabe.
"""

try:
    response_lehrbuch = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_lehrbuch,
        config=types.GenerateContentConfig(
            system_instruction=sys_inst_lehrbuch,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    with open(OUTPUT_LEHRBUCH, "w", encoding="utf-8") as f:
        f.write(response_lehrbuch.text)
    print(f"Lehrbuchausgabe erfolgreich generiert: {OUTPUT_LEHRBUCH}")
except Exception as e:
    print(f"Fehler in Phase 3: {e}")

print("\nAlle Phasen abgeschlossen.")
