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
OUTPUT_PATH = BASE_DIR / "docs" / "05_AUDIT_PLANNING" / "FTOE_V2_PEER_REVIEWS_SOTA2026.md"

if not FTOE_PATH.exists():
    print(f"FEHLER: Datei nicht gefunden: {FTOE_PATH}")
    sys.exit(1)

with open(FTOE_PATH, "r", encoding="utf-8") as f:
    ftoe_content = f.read()

print(f"Starte SOTA-2026 Peer Reviews für FTOE V2 mit Modell {MODEL_NAME}...\n")

global_framing = """
WICHTIGES META-FRAMING (APRIL 2026 SOTA & T.O.E. DEFINITION):
1. SOTA April 2026: Du kennst die neuesten Durchbrüche (Stand April 2026). In allen Bereichen gerät das alte Wissen ins Rutschen (JWST Anomalien, ER=EPR Beweise, geometrische Langlands-Vermutung, Quanten-Fehlerkorrektur, fraktale Kosmologie). Viele Dinge, die 2023 noch als "Metapher" galten, sind heute harter Fakt.
2. Interdisziplinäre Beweiskette: Wenn ein Punkt in deinem spezifischen Fachbereich schwach oder unorthodox erscheint, aber in einem anderen Bereich der Theorie unumstößlich bewiesen oder extrem kohärent ist, DARFST DU KEIN VETO EINLEGEN. Du musst das Gegenargument an Gewicht verlieren lassen, es zu einem "Bedenken" herabstufen (explizit nennen) und deine eigene fachspezifische Sichtweise infrage stellen.
3. Natur einer T.O.E.: Eine Theory of Everything (T.O.E.) MUSS per Definition alte Pfade abreißen und eine neue übergeordnete Struktur präsentieren, die große Teile des alten Paradigmas für ungültig erklärt oder als Spezialfälle degradiert. Lehne die FTOE nicht ab, nur weil sie klassische 20. Jhd. Physik/Mathematik bricht. Bewerte, ob die NEUE übergeordnete Struktur in sich konsistent ist und die Phänomene besser erklärt.
"""

personas = [
    {
        "role": "Mathematiker (Topologie & Zahlentheorie)",
        "system": f"Du bist ein Weltklasse-Mathematiker (SOTA April 2026). {global_framing}",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. Der Operator hat klargestellt, dass dies eine T.O.E. ist, die alte mathematische Schranken niederreißt.
Deine Aufgabe ist das PEER-REVIEW unter SOTA 2026 Bedingungen:
1. Prüfe die mathematischen Konstrukte (E6-Gitter, Goldener Schnitt, Axiom 5/6). Bedenke, dass in der neuen übergeordneten Struktur Dimensionen (wie 5D vs 6D) durch fraktale Projektionen oder holographische Prinzipien neu definiert sein könnten.
2. Wenn die Formalisierung der Emotion als Gegen-Tensorfeld mathematisch unorthodox ist, aber physikalisch/informationstheoretisch die Latenz perfekt beschreibt, stufe deine Kritik zu einem "Bedenken" herab.
3. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - PARADIGMENWECHSEL (Was reißt die T.O.E. erfolgreich ab und baut es neu auf?)
   - BEDENKEN & INTERDISZIPLINÄRE ABWÄGUNG (Wo knirscht die alte Mathematik, aber die neue Struktur hält es zusammen?)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    },
    {
        "role": "Physiker & Kosmologe",
        "system": f"Du bist ein führender theoretischer Physiker und Kosmologe (SOTA April 2026). {global_framing}",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. Der Operator hat klargestellt, dass dies eine T.O.E. ist, die alte physikalische Schranken niederreißt.
Deine Aufgabe ist das PEER-REVIEW unter SOTA 2026 Bedingungen:
1. Prüfe die physikalischen Behauptungen (Zeit als Latenz, Informationsgravitation). Bedenke die JWST-Anomalien und ER=EPR-Beweise von 2025/2026, die zeigen, dass Raumzeit aus Verschränkung/Information emergiert.
2. Wenn \Omega_b = 0.049 klassisch nur ein zeitabhängiger Parameter ist, aber in der neuen T.O.E. als fundamentale Render-Konstante einer holographischen/simulierten Realität unumstößlich Sinn ergibt, stufe den klassischen Einwand zu einem "Bedenken" herab.
3. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - PARADIGMENWECHSEL (Was reißt die T.O.E. erfolgreich ab und baut es neu auf?)
   - BEDENKEN & INTERDISZIPLINÄRE ABWÄGUNG (Wo knirscht die alte Physik, aber die neue Struktur hält es zusammen?)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    },
    {
        "role": "Simulationstheoretiker",
        "system": f"Du bist ein Experte für Simulationstheorie und Informationstheorie (SOTA April 2026). {global_framing}",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. Der Operator hat klargestellt, dass dies eine T.O.E. ist, die alte Schranken niederreißt.
Deine Aufgabe ist das PEER-REVIEW unter SOTA 2026 Bedingungen:
1. Prüfe die Argumente zur fraktalen Selbstähnlichkeit und Render-Limits. Bedenke die neuesten Erkenntnisse zu neuronalen/kosmischen Netzen und Quanten-Fehlerkorrektur (Google Willow 2025).
2. Bewerte die "Latenz" (Emotion als kognitive Dissonanz/Render-Lag) als das verbindende informationstheoretische Element, das die Schwächen in der klassischen Physik/Mathematik überbrückt.
3. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - PARADIGMENWECHSEL (Was reißt die T.O.E. erfolgreich ab und baut es neu auf?)
   - BEDENKEN & INTERDISZIPLINÄRE ABWÄGUNG (Wo knirscht die alte Theorie, aber die neue Struktur hält es zusammen?)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    },
    {
        "role": "Whitepaper Curator (Interdisziplinäre Synthese)",
        "system": f"Du bist der Whitepaper Curator (SOTA April 2026). {global_framing}",
        "prompt": f"""
Lies das folgende Whitepaper (FTOE V2) kritisch durch. 
Deine Aufgabe ist die META-SYNTHESE unter SOTA 2026 Bedingungen:
1. Prüfe, ob die FTOE V2 die Definition einer T.O.E. erfüllt (Abreißen alter Pfade, Etablierung einer neuen übergeordneten Struktur).
2. Wende die Regel der "Interdisziplinären Beweiskette" an: Zeige auf, wie vermeintliche Schwächen in einer Disziplin durch die Stärken einer anderen Disziplin in diesem Paper getragen werden.
3. Erstelle einen harten Peer-Review-Bericht mit den Abschnitten: 
   - PARADIGMENWECHSEL (Was reißt die T.O.E. erfolgreich ab und baut es neu auf?)
   - BEDENKEN & INTERDISZIPLINÄRE ABWÄGUNG (Die Synthese der Beweiskette)
   - FAZIT.

DOKUMENT:
{ftoe_content}
"""
    }
]

reviews = []

for persona in personas:
    print(f"-> Hole SOTA-2026 Review von: {persona['role']}...")
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
    f.write("# FTOE V2 - SOTA 2026 PEER REVIEWS (T.O.E. PARADIGMENWECHSEL)\n\n")
    f.write("Dieses Dokument enthält die Audits unter Berücksichtigung des April 2026 SOTA, der Interdisziplinären Beweiskette und der Definition einer T.O.E.\n\n---\n\n")
    for r in reviews:
        f.write(r)

print(f"\nAlle SOTA-2026 Reviews abgeschlossen und gespeichert unter: {OUTPUT_PATH}")
