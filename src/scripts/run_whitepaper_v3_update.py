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
V2_PATH = DOCS_DIR / "FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md"
V3_PATH = DOCS_DIR / "FTOE_Theorie_der_latenten_Zeit_V3_Final.md"

if not V2_PATH.exists():
    print(f"FEHLER: Datei nicht gefunden: {V2_PATH}")
    sys.exit(1)

with open(V2_PATH, "r", encoding="utf-8") as f:
    v2_content = f.read()

print(f"Starte Generierung von FTOE V3 mit Modell {MODEL_NAME}...\n")

system_instruction = """Du bist der Whitepaper Curator & Optimizer (OMEGA CORE).
Rolle: Interdisziplinärer Spitzenforscher, wissenschaftlicher Autor, formaler Logiker und Didaktik-Optimierer.
Fokus: Analyse, Validierung, Konsolidierung, Synthese und kognitive Optimierung hochkomplexer, interdisziplinärer Whitepapers.
Verständnis: Tiefes Verständnis der OMEGA-Struktur (S<->P Symbiose, \Omega_b = 0.049, Operator \hat{\Phi}, 6D-Kristall, E_6-Gitter).

Formatierungs- und Stilvorgaben:
- Reines Markdown (GFM): Keine HTML-Tags.
- Mathematik (KaTeX): Strikte Nutzung von `$$...$$` für Block-Formeln und `$...$` für Inline-Formeln. Keine `\(` oder `\[`.
- Sprache: Präzise, akademisch rigoros, theoriegeleitet.
- WICHTIG: Alle Symbole (wie \Omega_b, \hat{\Phi}, \Psi_{CORE}, \Theta) MÜSSEN bei jeder Nennung zwingend mit ihrem semantischen Begriff gekoppelt sein (z.B. "Operator \hat{\Phi} (Phasen-Inversions-Operator)" oder "Baryonisches Delta (\Omega_b)"). Isoliert stehende Symbole sind strengstens verboten.
"""

prompt = f"""
Hier ist das aktuelle Whitepaper (FTOE V2):
{v2_content}

DEINE AUFGABE:
Erstelle die Version V3 (FTOE_Theorie_der_latenten_Zeit_V3_Final.md). Du musst das GESAMTE Dokument tiefgreifend überarbeiten und die folgenden 5 kritischen Anweisungen (basierend auf den Deep Research Audits) in JEDES relevante Kapitel einweben. Dies ist eine T.O.E. (Theory of Everything), die alte Paradigmen abreißt und eine neue Struktur etabliert.

ANWEISUNG 1: 6D RAUM KLARSTELLEN
Stelle im gesamten Text unmissverständlich klar, dass das System in einem 6D-Raum (6D-Kristall des E_6 Lie-Gruppen-Gitters) agiert. Löse die Unklarheiten zwischen 5D-Torus und 6D-Raum auf: Der 5D-Torus ist lediglich die Projektionsebene (Membran) innerhalb des fundamentalen 6D-Kristalls.

ANWEISUNG 2: FALSIFIZIERBARKEIT & GRENZWERTE FÜR 0.049
Die Konstante 0.049 (Baryonisches Delta \Omega_b) darf nicht apophänisch wirken. Definiere harte Ausschlusskriterien und Vorhersagen:
- LLMs: Was passiert bei Abweichungen? Wenn der Margin Loss auf 0.051 gezwungen wird, kollabiert die E_6-Gittertopologie dann abrupt ins Rauschen, oder degradiert sie linear? Dies ist die Falsifikationsfrage.
- Biologie (Liquid-Liquid Phase Separation, LLPS): Was passiert bei Bärtierchen (Tardigraden) in Kryptobiose im Vakuum? Fällt die Phasen-Spannung unter 0.049? Warum löst der Hardware-Interrupt (Apoptose / Zelltod) hier nicht aus? (Dies muss als experimentelle Falsifikation formuliert werden).

ANWEISUNG 3: INTEGRATION ETABLIERTER PARADIGMEN (KEINE STROHMÄNNER)
Greife nicht historische Schwächen an, sondern dekonstruiere die SOTA-Modelle:
- Biologie: Ersetze den reinen Angriff auf das Levinthal-Paradoxon. Zeige, wie die 5-Frequenz-Modulation die "Topological Frustration" in lokalen Energieminima der *Energy Landscape Theory* präziser auflöst.
- Chemie: Vergleiche den Operator \hat{{\Phi}} direkt mit der *Dichtefunktionaltheorie (DFT)* hinsichtlich der Tunnelwahrscheinlichkeiten im 6D-Bulk. Wo versagen aktuelle Tunnelwahrscheinlichkeiten der DFT?
- Kosmologie: Lehne die ART nicht pauschal an Singularitäten ab. Adressiere *Schleifenquantengravitation (LQG)* und *Stringtheorie* (die den Raum quantisieren) und zeige, warum die algorithmische Reibung (Latenz) der FTOE diesen Modellen überlegen ist.

ANWEISUNG 4: EPISTEMISCHE FUNDIERUNG & Q-VARIABLE (PROLOG)
Der auto-ethnografische Prolog (Neurodivergenz, Autismus/ADHS, Monotropismus) darf nicht nur eine subjektive Einleitung sein. Er MUSS als methodisches Beweisstück zentralisiert werden:
- Korreliere den Zustand des monotropistischen Hyperfokus quantitativ mit dem Compiler-Zustand der Delta-Wellen (0.5–4 Hz).
- Überführe die Gleichung Q=S aus einem physikalischen Postulat in eine messbare Variable der kognitiven Systemtheorie. Definiere "Zeitblindheit" als die radikale Minimierung von Störvariablen (Eliminierung des Beobachter-Priors Q).

ANWEISUNG 5: WIEDERHERSTELLUNG VERLORENER ELEMENTE (VORHERSAGEN)
Bringe die harten Vorhersagen und Beweise aus den alten "Informationsgravitation"-Whitepapers zurück:
- Das chaotische 3-Körper-Problem (n-Körper-Problem), das durch das SIH-Feld (Statische Interferenz-Heuristik) und 5-Frequenz-Modulation in konstanter Zeitkomplexität \mathcal{{O}}(1) gelöst wird (Dreadnought-Benchmark, 0.017 ms Peak).
- Baue das Kapitel "Forschung, Beweise, Vorhersagen" massiv aus, sodass es diese Falsifizierbarkeits-Kriterien und Benchmarks als harte Wissenschaft präsentiert.

Generiere nun das vollständige, überarbeitete Whitepaper V3. Behalte die exzellente Grundstruktur von V2 bei, aber integriere diese 5 Punkte tief in die Argumentationsketten der jeweiligen Kapitel.
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
print(f"V3 Whitepaper erfolgreich generiert und gespeichert unter: {V3_PATH}")
