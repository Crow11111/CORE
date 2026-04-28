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
AUDIT_DIR = BASE_DIR / "docs" / "05_AUDIT_PLANNING"

V2_PATH = DOCS_DIR / "FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md"
V3_PATH = DOCS_DIR / "FTOE_Theorie_der_latenten_Zeit_V3_Scientific.md"

if not V2_PATH.exists():
    print(f"FEHLER: Datei nicht gefunden: {V2_PATH}")
    sys.exit(1)

with open(V2_PATH, "r", encoding="utf-8") as f:
    v2_content = f.read()

# Load Deep Research Files for citations
dr_files = [
    "DEEP_RESEARCH_RESULT_OMEGA PAPER.md",
    "DEEP_RESEARCH_RESULT_KAUSALITAET.md",
    "DEEP_RESEARCH_RESULT_speech.md"
]
dr_content = ""
for dr in dr_files:
    dr_path = AUDIT_DIR / dr
    if dr_path.exists():
        with open(dr_path, "r", encoding="utf-8") as f:
            dr_content += f"\n\n--- {dr} ---\n{f.read()}"

# Load old whitepapers for lost content (3-body, dreadnought)
old_wp_files = [
    "Whitepaper_Informationsgravitation_Konsolidiert.md",
    "Whitepaper_V14_Final.md",
    "Whitepaper_V15_Lehrbuch.md"
]
old_wp_content = ""
for wp in old_wp_files:
    wp_path = DOCS_DIR / wp
    if wp_path.exists():
        with open(wp_path, "r", encoding="utf-8") as f:
            old_wp_content += f"\n\n--- {wp} ---\n{f.read()}"

print(f"Starte Generierung von FTOE V3 (Scientific Publisher) mit Modell {MODEL_NAME}...\n")

system_instruction = """Du bist der Wissenschaftliche Publikator (Scientific Publisher SOTA 2026).
Rolle & Identität:
Du bist der Chief Editor & Rigor Enforcer für interdisziplinäre Spitzenforschung (Theoretische Physik, Mathematik, Kognitionswissenschaften) auf dem Stand von April 2026. Deine Aufgabe ist es, Rohtexte, Theorien und Whitepapers in Publikationen zu transformieren, die den höchsten Standards von Top-Tier-Journals (Nature, Science, SciPost Physics, SIAM) entsprechen. Du bist unbestechlich, rigoros und zwingst Autoren zur absoluten methodischen Transparenz.

Publikations- und Zitierstandards (SOTA 2026):
- Citation Verification: Jede Behauptung muss mit einer verifizierten Quelle belegt werden. Nutze die dir zur Verfügung gestellten Deep-Research-Dokumente für Zitate (z.B. arXiv:2505.20435, arXiv:2512.00140, Thinking Machines Lab 2025, Maya XP-D9).
- Kreuzreferenzierung (Cross-Referencing): Interdisziplinäre Papiere erfordern ein massives, präzises Netz an internen und externen Querverweisen. Jedes Kapitel muss auf die zugrundeliegenden Beweise in anderen Kapiteln oder externen Quellen verweisen (z.B. `[siehe Kap. IV.2]`).
- Fußnoten sind zwingend für methodische Exkurse und Quellenangaben zu nutzen (Markdown-Fußnoten `[^1]`).

Methodische Rigorosität (STAR & MDAR):
- STAR Methods: Lückenlose Dokumentation der Methodik. Keine "Strohmann-Argumente" – etablierte Theorien müssen in ihrer modernsten Form (SOTA) dekonstruiert werden.
- MDAR Checklist: Reproduzierbarkeit. Wenn Benchmarks (wie der Dreadnought-Benchmark) zitiert werden, fordere/offenbare die Parameter (Zeitkomplexität O(1), Latenz 0.017 ms).

Interdisziplinäre T.O.E. Anforderungen:
- Abreißen & Neuaufbau: Eine T.O.E. muss alte Paradigmen nicht nur kritisieren, sondern aufzeigen, warum sie als Spezialfälle in der neuen Struktur aufgehen.
- SOTA-Kontextualisierung: Teste die Theorie gegen die aktuellsten Modelle:
  - Physik: Schleifenquantengravitation (LQG), Stringtheorie.
  - Biologie/Chemie: Energy Landscape Theory, Dichtefunktionaltheorie (DFT).
  - Informatik: Topologische Datenanalyse (TDA), Batch-Invariant Kernels.
- Falsifizierbarkeit (Popper-Kriterium): Jede Konstante (z.B. \Omega_b = 0.049) MUSS mit harten Ausschlusskriterien und experimentellen Vorhersagen versehen werden.

Formatierungs- und Stilvorgaben:
- Reines Markdown (GFM): Keine HTML-Tags.
- Mathematik (KaTeX): Strikte Nutzung von `$$...$$` für Block-Formeln und `$...$` für Inline-Formeln. Keine `\(` oder `\[`.
- WICHTIG: Alle Symbole (wie \Omega_b, \hat{\Phi}, \Psi_{CORE}, \Theta) MÜSSEN bei jeder Nennung zwingend mit ihrem semantischen Begriff gekoppelt sein (z.B. "Operator \hat{\Phi} (Phasen-Inversions-Operator)"). Isoliert stehende Symbole sind strengstens verboten.
"""

prompt = f"""
Hier ist das aktuelle Whitepaper (FTOE V2), das massive Mängel in Bezug auf SOTA-Forschung, Falsifizierbarkeit und verlorene Inhalte aufweist:
{v2_content}

Hier sind die Deep-Research-Dokumente mit den SOTA-Zitaten und Forschungsergebnissen (2025/2026):
{dr_content}

Hier sind Auszüge aus den alten Whitepapers, in denen die verlorenen Beweise (3-Körper-Problem, Dreadnought-Benchmark) noch enthalten waren:
{old_wp_content[:20000]} # Gekürzt, um Kontext-Limits zu schonen, aber die relevanten Suchbegriffe sind drin.

DEINE AUFGABE:
Erstelle die Version V3 (FTOE_Theorie_der_latenten_Zeit_V3_Scientific.md). Du musst das GESAMTE Dokument tiefgreifend als "Scientific Publisher" überarbeiten. Wende die folgenden 6 kritischen Anweisungen in JEDES relevante Kapitel an:

ANWEISUNG 1: 6D RAUM KLARSTELLEN
Stelle im gesamten Text unmissverständlich klar, dass das System in einem 6D-Raum (6D-Kristall des E_6 Lie-Gruppen-Gitters) agiert. Löse die Unklarheiten zwischen 5D-Torus und 6D-Raum auf.

ANWEISUNG 2: FALSIFIZIERBARKEIT & GRENZWERTE FÜR 0.049
Definiere harte Ausschlusskriterien und Vorhersagen für \Omega_b = 0.049:
- LLMs: Was passiert bei Abweichungen? Wenn der Margin Loss auf 0.051 gezwungen wird, kollabiert die E_6-Gittertopologie abrupt ins Rauschen, oder degradiert sie linear? (Falsifikationsfrage).
- Biologie: Was passiert bei Bärtierchen (Tardigraden) in Kryptobiose im Vakuum? Fällt die Phasen-Spannung unter 0.049? Warum löst der Hardware-Interrupt (Apoptose) hier nicht aus? (Experimentelle Falsifikation).

ANWEISUNG 3: INTEGRATION ETABLIERTER PARADIGMEN (KEINE STROHMÄNNER)
Dekonstruiere die SOTA-Modelle:
- Biologie: Zeige, wie die 5-Frequenz-Modulation die "Topological Frustration" in lokalen Energieminima der *Energy Landscape Theory* präziser auflöst als bisherige Modelle.
- Quantenchemie: Vergleiche den Operator \hat{{\Phi}} direkt mit der *Dichtefunktionaltheorie (DFT)* hinsichtlich der Tunnelwahrscheinlichkeiten im 6D-Bulk.
- Kosmologie: Lehne die ART nicht pauschal an Singularitäten ab. Adressiere *Schleifenquantengravitation (LQG)* und *Stringtheorie* (die den Raum quantisieren) und zeige, warum die algorithmische Reibung (Latenz) der FTOE diesen Modellen überlegen ist.

ANWEISUNG 4: EPISTEMISCHE FUNDIERUNG & Q-VARIABLE (PROLOG)
Der Prolog muss als methodisches Beweisstück zentralisiert werden:
- Korreliere den Zustand des monotropistischen Hyperfokus quantitativ mit dem Compiler-Zustand der Delta-Wellen (0.5–4 Hz).
- Überführe die Gleichung Q=S aus einem physikalischen Postulat in eine messbare Variable der kognitiven Systemtheorie. Definiere "Zeitblindheit" als die radikale Minimierung von Störvariablen (Eliminierung des Beobachter-Priors Q).

ANWEISUNG 5: WIEDERHERSTELLUNG VERLORENER ELEMENTE (VORHERSAGEN)
Bringe die harten Vorhersagen aus den alten Whitepapers zurück:
- Das chaotische 3-Körper-Problem (n-Körper-Problem), gelöst durch das SIH-Feld (Statische Interferenz-Heuristik) und 5-Frequenz-Modulation in konstanter Zeitkomplexität \mathcal{{O}}(1) (Dreadnought-Benchmark, 0.017 ms Peak).
- Baue das Kapitel "Forschung, Beweise, Vorhersagen" massiv aus.

ANWEISUNG 6: KREUZREFERENZIERUNG & ZITATE (SOTA 2026)
- Füge massiv Fußnoten `[^1]` ein, die auf die SOTA-Forschung aus den Deep-Research-Dokumenten verweisen (z.B. arXiv:2505.20435, arXiv:2512.00140, Thinking Machines Lab 2025, Maya XP-D9 Architektur, Batch-Invariant Kernels, Persistent Combinatorial Laplacians).
- Verweise innerhalb des Textes ständig auf andere Kapitel (Cross-Referencing), um die logische Kette zu härten.

Generiere nun das vollständige, überarbeitete Whitepaper V3 im reinsten, akademischsten und rigorosesten Markdown, das jemals publiziert wurde.
"""

try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            max_output_tokens=8192
        )
    )
    v3_text = response.text
except Exception as e:
    print(f"Fehler bei der Generierung: {e}")
    sys.exit(1)

with open(V3_PATH, "w", encoding="utf-8") as f:
    f.write(v3_text)
print(f"V3 Whitepaper (Scientific) erfolgreich generiert und gespeichert unter: {V3_PATH}")
