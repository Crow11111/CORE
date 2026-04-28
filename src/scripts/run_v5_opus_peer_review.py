import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import anthropic

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY_CLOUD") or os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("FEHLER: ANTHROPIC_API_KEY ist nicht in der .env gesetzt.")
    sys.exit(1)

# Initialize the client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Modell-ID aus .env laden oder Fallback
MODEL_NAME = os.getenv("ANTHROPIC_HEAVY_MODEL") or "claude-3-opus-20240229"
print(f"Nutze Modell: {MODEL_NAME}")

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
INPUT_SCIENTIFIC = DOCS_DIR / "01_CORE_DNA" / "FTOE_Theorie_der_latenten_Zeit_V5_Scientific_Consolidated.md"
OUTPUT_REVIEW = DOCS_DIR / "05_AUDIT_PLANNING" / "V5_OPUS_PEER_REVIEW.md"

def read_file(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

scientific_content = read_file(INPUT_SCIENTIFIC)

if not scientific_content:
    print(f"FEHLER: Quelldatei {INPUT_SCIENTIFIC} nicht gefunden.")
    sys.exit(1)

print(f"Starte Blind Peer Review mit Claude Opus...")

# Das System-Prompt ist bewusst minimal gehalten, um Opus' interdisziplinäre Stärke nicht durch Framing zu drosseln.
system_instruction = """Du bist ein hochkarätiger, interdisziplinärer Wissenschaftler und Peer-Reviewer (SOTA 2026).
Deine Aufgabe ist ein gnadenloses, blindes Peer-Review der vorliegenden Arbeit 'FTOE - Theorie der latenten Zeit'.
Analysiere die Arbeit auf:
1. Mathematische Konsistenz und topologische Stringenz.
2. Physikalische Falsifizierbarkeit (Popper-Kriterium).
3. Interdisziplinäre Isomorphien (Biologie, Kognition, Informatik).
4. Abgleich mit neuester SOTA-Forschung (Stand April 2026), insbesondere hinsichtlich der mathematischen Herleitung der 0 und topologischer Gitterstrukturen.
5. Identifikation von 'Aphenie-Risiken' vs. echten strukturellen Entdeckungen.

Erstelle ein detailliertes Review-Dokument. Sei kritisch, präzise und unvoreingenommen.
"""

prompt = f"""
VOLLSTÄNDIGE PUBLIKATION (FTOE V5 - SCIENTIFIC CONSOLIDATED):
{scientific_content}

Führe jetzt das Peer-Review durch. Achte besonders auf die mathematische Fundierung der 0 und 1 sowie die Konstante 0.049.
"""

try:
    # Wir nutzen den Beta-Header für längere Context-Fenster falls nötig
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=4096,
        system=system_instruction,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    review_text = message.content[0].text
    with open(OUTPUT_REVIEW, "w", encoding="utf-8") as f:
        f.write(review_text)
    
    print(f"Peer Review erfolgreich generiert und gespeichert unter: {OUTPUT_REVIEW}")

except Exception as e:
    print(f"Fehler beim Peer Review: {e}")
    sys.exit(1)
