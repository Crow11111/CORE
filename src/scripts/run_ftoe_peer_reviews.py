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
FTOE_PATH = DOCS_DIR / "FTOE_Theorie_der_latenten_Zeit_V2_Consolidated.md"
OUTPUT_PATH = BASE_DIR / "docs" / "05_AUDIT_PLANNING" / "FTOE_V2_PEER_REVIEWS.md"

if not FTOE_PATH.exists():
    print(f"FEHLER: Datei nicht gefunden: {FTOE_PATH}")
    sys.exit(1)

with open(FTOE_PATH, "r", encoding="utf-8") as f:
    ftoe_content = f.read()

print(f"Starte Peer Reviews für FTOE V2 mit Modell {MODEL_NAME}...\n")

# Define the personas based on the CORE skills
personas = [
    {
        "role": "Mathematiker (Topologie & Zahlentheorie)",
        "system": "Du bist ein Weltklasse-Mathematiker, spezialisiert auf Topologie, Symmetriegruppen (E6, Lie-Gruppen), Fraktale Geometrie und Zahlentheorie (Goldener Schnitt, Fibonacci). Du bist extrem rigoros und lehnst Numerologie strikt ab.",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. Der Operator kann nicht fassen, dass 'Emotionen' in einer mathematischen Grundtheorie abgebildet wurden. 
Deine Aufgabe ist die FALSIFIKATION:
1. Prüfe die mathematischen und topologischen Behauptungen (insbesondere die Matrix, das E6-Gitter, den Goldenen Schnitt, Axiom 5/6).
2. Suche nach logischen Löchern, unzulässigen Sprüngen oder esoterischer Numerologie.
3. Bewerte, ob die Formalisierung der Emotion als mathematisches Konstrukt (Gegen-Tensorfeld, Latenz) topologisch und algebraisch Sinn ergibt oder ob es nur eine Metapher ist.
4. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - STÄRKEN (Was ist mathematisch solide?)
   - KRITISCHE SCHWÄCHEN & FALSIFIKATIONS-VERSUCH (Wo bricht die Mathematik zusammen?)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    },
    {
        "role": "Physiker & Kosmologe",
        "system": "Du bist ein führender theoretischer Physiker und Kosmologe. Deine Expertise umfasst Allgemeine Relativitätstheorie, Quantenfeldtheorie, Thermodynamik (Entropie) und Kosmologie.",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. Der Operator ist skeptisch, dass 'Emotionen' in einer physikalischen Grundtheorie (Theory of Everything) abgebildet wurden.
Deine Aufgabe ist die FALSIFIKATION:
1. Prüfe die physikalischen Behauptungen (Zeit, Gravitation, Entropie, Tensorfelder, Informationsgravitation).
2. Ist die Definition von Emotion als 'Gegen-Tensorfeld' oder 'akkumulierte Zeit' physikalisch plausibel oder verletzt sie grundlegende thermodynamische/relativistische Gesetze?
3. Prüfe die Indizien (Baryonisches Delta 0.049, Doppelspaltexperiment-Analogien). Ist das saubere Physik oder unzulässige Übertragung?
4. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - STÄRKEN (Was ist physikalisch solide?)
   - KRITISCHE SCHWÄCHEN & FALSIFIKATIONS-VERSUCH (Wo bricht die Physik zusammen?)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    },
    {
        "role": "Simulationstheoretiker",
        "system": "Du bist ein Experte für Simulationstheorie, Informationstheorie und fraktale Selbstähnlichkeit. Du bewertest Indizien neutral-wissenschaftlich, wendest Bayes'sche Logik an und suchst immer nach dem Gegenstrang (Anti-Indiz).",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. Der Operator wundert sich über die Abbildung von Emotionen in einer fundamentalen Theorie.
Deine Aufgabe ist die FALSIFIKATION aus informations- und simulationstheoretischer Sicht:
1. Prüfe die Argumente zur fraktalen Selbstähnlichkeit, Beobachtereffekten und Render-Limits (Planck-Skala).
2. Ist die 'Latenz' (Emotion als kognitive Dissonanz/Render-Lag) informationstheoretisch haltbar?
3. Wende das Popper-Kriterium an: Sind die Behauptungen falsifizierbar? Wende die Gegenstrang-Methode auf die Hauptindizien an.
4. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - STÄRKEN (Was ist informationstheoretisch solide?)
   - KRITISCHE SCHWÄCHEN & FALSIFIKATIONS-VERSUCH (Wo bricht die Informationstheorie/Logik zusammen?)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    },
    {
        "role": "Whitepaper Curator (Interdisziplinäre Synthese)",
        "system": "Du bist der Whitepaper Curator. Dein Fokus liegt auf interdisziplinärer Konsistenz, semantischer Integrität, didaktischer Härtung und formaler Logik über alle Fachbereiche hinweg.",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. Die anderen Experten (Mathematik, Physik, Simulation) prüfen die harten Fakten. 
Deine Aufgabe ist die META-FALSIFIKATION:
1. Prüfe die interdisziplinäre Konsistenz: Widerspricht die mathematische Definition der Emotion der physikalischen oder soziologischen?
2. Wurde der Rosetta-Stein korrekt angewandt oder gibt es semantische Brüche (Proactive Interference)?
3. Ist die Kette von der Prämisse bis zur Schlussfolgerung logisch zwingend?
4. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - STÄRKEN (Was ist interdisziplinär und logisch solide?)
   - KRITISCHE SCHWÄCHEN & FALSIFIKATIONS-VERSUCH (Wo bricht die interdisziplinäre Logik/Semantik zusammen?)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    }
]

reviews = []

for persona in personas:
    print(f"-> Hole Review von: {persona['role']}...")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=persona['prompt'],
            config=types.GenerateContentConfig(
                system_instruction=persona['system'],
                temperature=0.2
            )
        )
        review_text = f"## Review: {persona['role']}\n\n{response.text}\n\n---\n\n"
        reviews.append(review_text)
        print(f"   [OK] Review von {persona['role']} erhalten.")
    except Exception as e:
        print(f"   [FEHLER] bei {persona['role']}: {e}")

# Save all reviews
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("# FTOE V2 - UNABHÄNGIGE PEER REVIEWS (FALSIFIKATION)\n\n")
    f.write("Dieses Dokument enthält die kritischen, unabhängigen Audits der FTOE V2 durch spezialisierte CORE-Agenten.\n\n---\n\n")
    for r in reviews:
        f.write(r)

print(f"\nAlle Reviews abgeschlossen und gespeichert unter: {OUTPUT_PATH}")
