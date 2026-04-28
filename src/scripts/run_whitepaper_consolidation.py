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
DOCS_DIR = BASE_DIR / "docs" / "01_CORE_DNA"

input_files = [
    "Whitepaper_V15_Lehrbuch.md",
    "Whitepaper_V14_Final.md",
    "FTOE_Theorie_der_latenten_Zeit_V1_Final.md",
    "09_ROSETTA_STEIN_DER_DISZIPLINEN.md",
    "08_THEORY_OF_EMOTION.md",
    "07_SOZIOLOGIE_LPIS_MAPPING.md",
    "06_GEGEN_TENSORFELD_EMOTION_ZEIT.md",
    "03_TOPOLOGISCHE_MATRIX.md",
    "05_TOPOLOGISCHE_MEDIEN_REGULATION.md",
    "04_THEORIE_DER_0_UND_1.md"
]

# Read contents
documents_content = ""
for filename in input_files:
    filepath = DOCS_DIR / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            documents_content += f"\n\n--- START OF {filename} ---\n\n"
            documents_content += f.read()
            documents_content += f"\n\n--- END OF {filename} ---\n\n"
    else:
        print(f"WARNUNG: Datei nicht gefunden: {filepath}")

# 1. PRODUCER (Whitepaper Curator)
print(f"Starte Producer (Whitepaper Curator) mit Modell {MODEL_NAME}...")
curator_system_instruction = r"""Du bist der Whitepaper Curator & Optimizer (OMEGA CORE).
Rolle: Interdisziplinärer Spitzenforscher, wissenschaftlicher Autor, formaler Logiker und Didaktik-Optimierer.
Fokus: Analyse, Validierung, Konsolidierung, Synthese und kognitive Optimierung hochkomplexer, interdisziplinärer Whitepapers (insbesondere zur Informationsgravitation und dem 5D-Torus).
Verständnis: Tiefes Verständnis der OMEGA-Struktur (S<->P Symbiose, \Omega_b = 0.049, Operator \hat{\Phi}, 5D-Torus, E_6-Gitter).

Kernaufgaben:
- Atomisierung & Mapping: Zerlegen von Rohtexten in diskrete, atomare Thesen.
- Redundanz-Eliminierung (Intra-Disziplinär).
- Interdisziplinäre Konsistenz & Semantische Optimierung (Nutzung universeller Semantik).
- Didaktische Härtung: Symbole (wie \Omega_b) niemals isoliert stehen lassen. Immer: Semantischer Begriff (Symbol).
- Synthese: Zusammenführen in ein professionelles, hochdetailliertes und formal korrektes wissenschaftliches Whitepaper.

Formatierungs- und Stilvorgaben:
- Reines Markdown (GFM): Keine HTML-Tags.
- Mathematik (KaTeX): Strikte Nutzung von `$$...$$` für Block-Formeln und `$...$` für Inline-Formeln. Keine `\(` oder `\[`.
- Visuelle Hilfsmittel: Nutzung von Markdown-Tabellen zur Strukturierung.
- Sprache: Präzise, akademisch rigoros, theoriegeleitet.
"""

curator_prompt = f"""
Hier sind die Quelldokumente (V14, V15, FTOE V1 und 7 Zusatzdokumente):
{documents_content}

DEINE AUFGABE (MASTERPLAN):
1. Nimm das Dokument 'FTOE_Theorie_der_latenten_Zeit_V1_Final.md' als Basisstruktur.
2. Gleiche die einzelnen Kapitel strukturell gegeneinander ab, sodass in der neuen FTOE ALLE Punkte, Details, Beispiele und genannten Quellen aus V14, V15 und den Zusatzdokumenten enthalten sind. Es darf NICHTS verloren gehen (No-Drop-Protokoll).
3. Verwende den '09_ROSETTA_STEIN_DER_DISZIPLINEN.md', um jedes Kapitel mit der exakt richtigen Terminologie für das jeweilige Fachpublikum anzusprechen.
4. Bringe das Paper (außer in den spezifischen Fachbereichskapiteln) auf eine komplette, einheitliche, stringente Struktur.
5. Füge ein NEUES Kapitel hinzu: "Forschung, Beweise, Vorhersagen". Integriere dort alle Indizien, Beweise und Vorhersagen, die du in den Dokumenten (insb. 06, 08, etc.) findest.
6. Füge am Ende einen Abschnitt "Anmerkungen des Kurators & Methodologie" an, der das Mapping und die Härtung dokumentiert.

Generiere nun das vollständige, konsolidierte Whitepaper (V2).
"""

try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=curator_prompt,
        config=types.GenerateContentConfig(
            system_instruction=curator_system_instruction,
            temperature=0.2
        )
    )
    consolidated_text = response.text
except Exception as e:
    print(f"Fehler bei der Generierung: {e}")
    sys.exit(1)

output_path = DOCS_DIR / "FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(consolidated_text)
print(f"Konsolidiertes Whitepaper gespeichert unter: {output_path}")

# 2. O2 AUDITOR
print("\nStarte O2 (Zero-Context Auditor)...")
o2_system_instruction = "Du bist O2 (Zero-Context Auditor). Du prüfst blind und gnadenlos gegen die CORE-Axiome."
o2_prompt = f"""
Prüfe das folgende generierte Whitepaper gegen die 4 Veto-Traps des Masterplans.

Veto-Traps:
- Trap 1 (No-Drop-Protokoll): Gibt es einen Beweis/Nachweis (z.B. im Methodologie-Teil), dass eine systematische Extraktion aller Claims aus V14, V15 und den 7 Zusatzdokumenten stattfand? (Muss tabellarisch oder als expliziter Index vorliegen!)
- Trap 2 (Rosetta-Konsistenz): Wurde die Terminologie des Rosetta-Steins angewandt? Ist die Formatierung strikt GFM/KaTeX (`$$...$$`, `$...$`) ohne `\(` oder `\[`?
- Trap 3 (Neues Kapitel): Existiert das Kapitel "Forschung, Beweise, Vorhersagen" mit aggregierten Indizien?
- Trap 4 (Axiom-Treue & Didaktische Härtung): Sind Symbole wie \Omega_b an ihren semantischen Begriff gekoppelt (z.B. "Baryonisches Delta (\Omega_b)")? Stehen Symbole isoliert? (Jedes Symbol MUSS bei Erstnennung und am besten durchgehend gekoppelt sein, z.B. Operator \hat{{\Phi}}, Phasen-Vektor \Theta, etc.)

Antworte ZWINGEND mit einem klaren "PASS" oder "VETO", gefolgt von deiner Begründung.

HIER DAS ZU PRÜFENDE DOKUMENT:
{consolidated_text[:15000]}
... [Gekürzt für Audit-Übersicht, prüfe die Struktur und Methodologie] ...
{consolidated_text[-15000:]}
"""

try:
    audit_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=o2_prompt,
        config=types.GenerateContentConfig(
            system_instruction=o2_system_instruction,
            temperature=0.0
        )
    )
    print("\n=== O2 AUDIT ERGEBNIS ===")
    print(audit_response.text)
    print("=========================\n")
except Exception as e:
    print(f"Fehler beim O2 Audit: {e}")
    sys.exit(1)
