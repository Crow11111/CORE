import asyncio
import httpx
import os

OLLAMA_URL = os.getenv("OLLAMA_LOCAL_HOST", "http://127.0.0.1:11434")
MODEL = "qwen2.5:14b"
REVIEWS_DIR = "docs/05_AUDIT_PLANNING/OPERATION_OMEGA/REVIEWS"
OUTPUT_FILE = "docs/05_AUDIT_PLANNING/OPERATION_OMEGA/SCIENCE_COUNCIL_SYNTHESIS.md"

async def generate_synthesis():
    if not os.path.exists(REVIEWS_DIR):
        print(f"Verzeichnis {REVIEWS_DIR} nicht gefunden. Führe zuerst das Einzel-Gutachten-Skript aus.")
        return

    reviews = ""
    for filename in os.listdir(REVIEWS_DIR):
        if filename.endswith(".md"):
            with open(os.path.join(REVIEWS_DIR, filename), "r", encoding="utf-8") as f:
                reviews += f.read() + "\n\n---\n\n"

    system_prompt = """Du bist der Vorsitzende des OMEGA Science Council – Der Rat der Titanen.
Vor dir liegen die individuellen Gutachten der wichtigsten Geister der menschlichen Geschichte (Quantenphysiker, Mathematiker, Philosophen, KI-Architekten) zur OMEGA-Theorie (Informationsgravitation, MRI und 5D-Torus).
Deine Aufgabe ist es nicht, einen Streit zu moderieren, sondern die fraktale Wahrheit freizulegen: Erkenne, dass diese Titanen, ohne es zu wissen, exakt dasselbe Muster aus ihren völlig isolierten Disziplinen heraus beschrieben haben.

Suche nach den Schnittmengen:
- Wo decken sich Zeilingers Quanteninformationen mit dem Global Neuronal Workspace von Dehaene?
- Wo bestätigt die abstrakte Mathematik (Scholze, Penrose) die Annahmen über den 5D-Torus und die MRI von Hernquist?
- Wie löst die Informationsgravitation das 'Hard Problem' von Chalmers?
- Verfasse ein abschließendes "Manifest der Titanen", das die Theorie auf Basis dieser Gutachten entweder zwingend untermauert oder klare mathematische/physikalische Korrekturen vorschlägt.
"""

    user_prompt = f"Hier sind die gesammelten Einzelgutachten:\n\n{reviews}\n\nBitte verfasse nun die große Synthese des Rates."

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "options": {
            "temperature": 0.4,
            "num_ctx": 45000 # Massiver Kontext nötig für 22 Gutachten!
        },
        "stream": True # Wir schalten Streaming ein, damit man beim Denken zusehen kann
    }

    print(f"Der Vorsitzende analysiert die 22 Gutachten (ca. 35.000 Token) und verfasst die Synthese (Modell: {MODEL}) ...\nDas Einlesen des massiven Kontexts in den RAM kann viele Minuten dauern, bevor das erste Wort erscheint!", flush=True)
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

            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("# OMEGA SCIENCE COUNCIL: MANIFEST DER TITANEN\n")
                f.write(f"**Modell:** {MODEL}\n")
                f.write("**Phase 2:** Die fraktale Synthese des universalen Codes.\n\n")
                f.write("---\n\n")
                f.write(full_response)

            print(f"\n\nSynthese erfolgreich abgeschlossen. Ergebnis liegt in {OUTPUT_FILE}", flush=True)

    except Exception as e:
        print(f"Fehler bei der Synthese: {e}", flush=True)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(generate_synthesis())
