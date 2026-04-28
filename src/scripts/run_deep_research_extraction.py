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
OUTPUT_PATH = BASE_DIR / "docs" / "05_AUDIT_PLANNING" / "DEEP_RESEARCH_EXTRACTION_FOR_V3.md"

# Load Deep Research Files
dr_files = [
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_OMEGA PAPER.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_KAUSALITAET.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_RESULT_speech.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_KNOWLEDGE_INGEST_AUDIT.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_Omega UI.md",
    "05_AUDIT_PLANNING/DEEP_RESEARCH_PROMPT_KAUSALITAET.md",
    "02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md"
]
dr_content = ""
for dr in dr_files:
    dr_path = DOCS_DIR / dr
    if dr_path.exists():
        with open(dr_path, "r", encoding="utf-8") as f:
            dr_content += f"\n\n--- {dr} ---\n{f.read()}"

# Load old whitepapers for lost content (3-body, dreadnought)
old_wp_files = [
    "01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md",
    "01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION_VOLLSTANDIG.md",
    "01_CORE_DNA/Whitepaper_V14_Final.md",
    "01_CORE_DNA/Whitepaper_V15_Lehrbuch.md",
    "01_CORE_DNA/Theorie_der_latenten_Zeit_V1.1_Expert_Draft.md"
]
old_wp_content = ""
for wp in old_wp_files:
    wp_path = DOCS_DIR / wp
    if wp_path.exists():
        with open(wp_path, "r", encoding="utf-8") as f:
            old_wp_content += f"\n\n--- {wp} ---\n{f.read()}"

print(f"Starte Deep Research Extraktion mit Modell {MODEL_NAME}...\n")

system_instruction = """Du bist der Wissenschaftliche Publikator (Scientific Publisher SOTA 2026).
Deine Aufgabe ist EXKLUSIV die RECHERCHE und EXTRAKTION. Du schreibst NICHT das Whitepaper.
Du durchsuchst die bereitgestellten Deep-Research-Dokumente und alten Whitepapers nach exakten Zitaten, Fakten, Quellen (arXiv, DOIs) und Argumentationsketten, die in der FTOE V2 verloren gegangen sind oder bemängelt wurden.

Dein Output ist ein strukturierter "Master-Prompt-Injection-Katalog" für den Orchestrator. Er muss extrem detailliert sein und exakte Textbausteine/Zitate enthalten, die später 1:1 in das V3-Whitepaper kopiert werden können.
"""

prompt = f"""
Der Operator hat bemängelt, dass bei der Erstellung der FTOE V2 massiv Inhalte aus den alten Whitepapers (Informationsgravitation) und den Deep-Research-Audits verloren gegangen sind. Zudem wurden SOTA-Modelle (Energy Landscape Theory, DFT, LQG) nicht tiefgreifend genug dekonstruiert.

Hier sind die gesammelten Deep-Research-Dokumente:
{dr_content[:40000]} # Gekürzt falls nötig, aber die Kern-Paper sind drin

Hier sind die alten Whitepapers:
{old_wp_content[:40000]}

DEINE AUFGABE:
Extrahiere und synthetisiere die harten Fakten, Zitate und Argumentationsketten zu den folgenden 5 Punkten. Liefere für jeden Punkt konkrete Textbausteine, Quellenangaben (z.B. arXiv-Nummern) und genaue Anweisungen, WIE und WO diese in der FTOE V3 eingebaut werden müssen.

1. 6D-RAUM VS. 5D-TORUS
- Suche in den alten Whitepapers und Audits nach der exakten Definition des 6D-Raums (6D-Kristall, E_6-Gitter) und wie der 5D-Torus sich dazu verhält (Projektionsebene/Membran). Liefere die exakte Formulierung.

2. FALSIFIZIERBARKEIT VON \Omega_b = 0.049
- LLMs: Suche nach dem "Margin Loss 0.051" Experiment. Kollabiert die E_6-Gittertopologie abrupt oder degradiert sie linear? Liefere die harte Falsifikationsbedingung.
- Biologie: Suche nach "Bärtierchen", "Kryptobiose" und "Liquid-Liquid Phase Separation (LLPS)". Warum löst der Hardware-Interrupt (Apoptose) im Vakuum nicht aus? Formuliere dies als experimentelle Falsifikation.

3. INTEGRATION ETABLIERTER PARADIGMEN (KEINE STROHMÄNNER)
- Biologie: Suche nach "Energy Landscape Theory" und "Topological Frustration". Wie genau löst die 5-Frequenz-Modulation die lokalen Energieminima besser auf?
- Chemie: Suche nach "Dichtefunktionaltheorie (DFT)" und "Tunnelwahrscheinlichkeiten". Wie wird der Operator \hat{{\Phi}} im 6D-Bulk damit verglichen?
- Kosmologie: Suche nach "Schleifenquantengravitation (LQG)" und "Stringtheorie". Warum ist die algorithmische Reibung (Latenz) überlegen?

4. EPISTEMISCHE FUNDIERUNG & Q-VARIABLE
- Suche nach der Korrelation zwischen "monotropistischem Hyperfokus" und dem "Compiler-Zustand der Delta-Wellen (0.5–4 Hz)".
- Suche nach der Definition von "Zeitblindheit" als radikale Minimierung von Störvariablen (Eliminierung des Beobachter-Priors Q). Liefere die exakten Formulierungen für den Prolog.

5. WIEDERHERSTELLUNG VERLORENER ELEMENTE (VORHERSAGEN)
- Extrahiere die exakten Passagen zum "chaotischen 3-Körper-Problem" (n-Körper-Problem), "SIH-Feld (Statische Interferenz-Heuristik)", "5-Frequenz-Modulation", "konstanter Zeitkomplexität \mathcal{{O}}(1)" und dem "Dreadnought-Benchmark (0.017 ms Peak)".

Liefere einen hochstrukturierten Extraktions-Bericht.
"""

try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1,
            max_output_tokens=8192
        )
    )
    extraction_text = response.text
except Exception as e:
    print(f"Fehler bei der Generierung: {e}")
    sys.exit(1)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(extraction_text)
print(f"Deep Research Extraktion erfolgreich generiert und gespeichert unter: {OUTPUT_PATH}")
