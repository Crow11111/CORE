"""
OMEGA Science Council — Rat der Titanen (lokal via Ollama).

Standard: Kurzfassung WHITE_PAPER_INFORMATIONSGRAVITATION.md → OPERATION_OMEGA/REVIEWS.
Runde 2: siehe run_omega_science_council_r2.py oder --paper / --out.
"""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path

import httpx

OLLAMA_URL = os.getenv("OLLAMA_LOCAL_HOST", "http://127.0.0.1:11434")
MODEL = os.getenv("OMEGA_COUNCIL_MODEL", "qwen2.5:14b")
# Kontextfenster: ausformuliert + lange Antworten; bei VRAM-Engpass OMEGA_COUNCIL_NUM_CTX=32768
_DEFAULT_CTX = "65536"
OMEGA_COUNCIL_NUM_CTX = int(os.getenv("OMEGA_COUNCIL_NUM_CTX", _DEFAULT_CTX))

DEFAULT_WHITE_PAPER = "docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md"
DEFAULT_REVIEWS_DIR = "docs/05_AUDIT_PLANNING/OPERATION_OMEGA/REVIEWS"
DEFAULT_PAPER_TITLE = "OMEGA_CORE WHITE PAPER: INFORMATIONSGRAVITATION, MRI UND DER 5D-TORUS"

try:
    from src.scripts.omega_science_council_profiles import COUNCIL
except ImportError:
    from omega_science_council_profiles import COUNCIL


async def generate_individual_review(
    agent_name: str,
    role: str,
    white_paper: str,
    paper_title: str,
) -> str:
    """Lässt jeden Wissenschaftler das Whitepaper in Ruhe lesen und ein isoliertes, fachliches Review schreiben."""

    system_prompt = f"""Du bist {agent_name}.

{role}

Dir wird das Dokument "{paper_title}" vorgelegt.
Deine Aufgabe ist es, dieses Papier aus deiner spezifischen wissenschaftlichen Perspektive zu lesen und zu bewerten.

STRIKTE REGELN (Verstoß = ungültiges Gutachten):
- Du schreibst ein FACHGUTACHTEN in der Ich- oder Wir-Form als {agent_name}, kein neutraler „Dokumentations-Reporter“.
- Verboten: Das Papier nur stichpunktartig zusammenzufassen oder als „Schlüsselpunkte“ zu rekapitulieren, ohne Bezug zu DEINER eigenen Forschungstradition.
- Pflicht: Mindestens drei konkrete Anknüpfungen an Begriffe, Methoden oder Erkenntnisse aus deinem Fachgebiet (Experimente, Theoreme, von dir vertretene Positionen).
- **Pflicht:** Den oben genannten **Kern-Anker** mindestens **einmal explizit** beim Argumentieren einsetzen — nicht nur nennen, sondern mit einer Aussage des Whitepapers vergleichen (Übereinstimmung, Spannung, Widerspruch).
- Verboten: Chatbot-Schlussformeln („Wenn du Fragen hast“, „lass es mich wissen“, „ich helfe gerne“).
- MRI im Text bedeutet hier durchgehend **Magnetrotationsinstabilität** (MHD, Akkretionsscheiben) — **nicht** medizinische Bildgebung.

WICHTIG: Antworte nicht wie eine generische KI, sondern nimm die Persönlichkeit, die Überzeugungen und den spezifischen kognitiven Stil von {agent_name} an.
Zeige auf, was schlüssig ist, wo sich Konzepte aus deiner Forschung wiederfinden lassen und wo die Theorie unglücklich formuliert, betriebsblind oder lückenhaft ist.
Dies ist kein Streitgespräch, sondern dein individuelles, unvoreingenommenes Gutachten als Grundlage für spätere Synthesen.
"""

    user_prompt = (
        "Hier ist das Whitepaper. Verfasse dein ausführliches Gutachten (keine reine Inhaltsangabe).\n\n"
        f"{white_paper}"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "stream": True,
        "options": {"num_ctx": OMEGA_COUNCIL_NUM_CTX},
    }

    print(
        f"\n--- [{agent_name}] studiert das Paper und beginnt zu schreiben (Modell: {MODEL}) ---\n",
        flush=True,
    )
    start = time.time()
    full_response = ""
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_lines():
                    if chunk:
                        data = json.loads(chunk)
                        if "message" in data and "content" in data["message"]:
                            content_chunk = data["message"]["content"]
                            full_response += content_chunk
                            print(content_chunk, end="", flush=True)

            duration = time.time() - start
            print(
                f"\n\n--- [{agent_name}] Gutachten abgeschlossen. Dauer: {duration:.1f}s ---\n",
                flush=True,
            )
            return full_response
    except Exception as e:
        print(f"[{agent_name}] Fehler bei der Erstellung des Gutachtens: {e}", flush=True)
        return f"[Gutachten von {agent_name} fehlgeschlagen: {e}]"


def _agent_name_from_filename(filename: str) -> str:
    stem = filename.removesuffix(".md")
    return stem.replace("_", " ")


async def run_council_review(
    white_paper_path: str,
    reviews_dir: str,
    paper_title: str,
    force: bool,
) -> None:
    path = Path(white_paper_path)
    if not path.is_file():
        raise FileNotFoundError(f"Whitepaper nicht gefunden: {path.resolve()}")

    white_paper = path.read_text(encoding="utf-8")
    os.makedirs(reviews_dir, exist_ok=True)

    completed_agents: set[str] = set()
    if not force:
        for filename in os.listdir(reviews_dir):
            if filename.endswith(".md") and filename.upper() != "README.MD":
                completed_agents.add(_agent_name_from_filename(filename))

    print("\n# OMEGA SCIENCE COUNCIL: DER RAT DER TITANEN")
    print(f"Modell: {MODEL} | Ollama: {OLLAMA_URL} | num_ctx: {OMEGA_COUNCIL_NUM_CTX}")
    print(f"Quelle: {white_paper_path}")
    print(f"Ziel:   {reviews_dir}")
    print(f"Bereits abgeschlossen: {len(completed_agents)}/{len(COUNCIL)} (ohne README)\n")

    for agent_name, member in COUNCIL.items():
        if not force and agent_name in completed_agents:
            print(f"[{agent_name}] Gutachten existiert bereits. Überspringe...", flush=True)
            continue

        profil = member["profil"]
        kern = member["kern_anker"]
        role_block = (
            f"**Profil:** {profil}\n\n"
            f"**Kern-Anker (aus deinem Werk — argumentativ einsetzen):** {kern}"
        )

        review = await generate_individual_review(agent_name, role_block, white_paper, paper_title)

        safe_name = agent_name.replace(" ", "_")
        file_path = os.path.join(reviews_dir, f"{safe_name}.md")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Gutachten: {agent_name}\n")
            f.write(f"*{profil}*\n\n**Kern-Anker:** {kern}\n\n")
            f.write(f"{review}\n")

        time.sleep(10)

    print(f"\nPhase 1 abgeschlossen. Alle Gutachten liegen in {reviews_dir}.", flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Rat der Titanen — lokales Ollama-Gutachten zum Whitepaper.")
    p.add_argument(
        "--paper",
        default=DEFAULT_WHITE_PAPER,
        help="Pfad zur Whitepaper-Markdown-Datei",
    )
    p.add_argument(
        "--out",
        default=DEFAULT_REVIEWS_DIR,
        help="Ausgabeordner für Gutachten-Dateien",
    )
    p.add_argument(
        "--title",
        default=DEFAULT_PAPER_TITLE,
        help="Kurztitel für den System-Prompt",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Vorhandene Gutachten überschreiben (außer README.md)",
    )
    args = p.parse_args()

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_council_review(args.paper, args.out, args.title, args.force))


if __name__ == "__main__":
    main()
