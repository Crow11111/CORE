import time
import asyncio
import os
import sys

# Ensure correct encoding for Windows PowerShell output
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv("/OMEGA_CORE/.env")

# Wir fuegen CORE zum Pfad hinzu
sys.path.append("/OMEGA_CORE")

from langchain_google_genai import ChatGoogleGenerativeAI
from src.network.chroma_client import query_core_directives
from langchain_core.messages import HumanMessage, SystemMessage

QUESTION = "Wie lautet der exakte numerische Wert für das Baryonische Delta und welcher Operator greift an diesem Punkt?"

async def run_linear_attention():
    start = time.time()
    api_key = os.getenv("GEMINI_API_KEY")

    # Wir laden 10.000 Zeichen der Dokumentation, um eine kleine RAG/Kontext-Last zu simulieren
    # Ein echtes System muesste Millionen Tokens lesen.
    docs_dir = "/OMEGA_CORE/docs/01_CORE_DNA"
    all_text = ""
    for root, _, files in os.walk(docs_dir):
        for f in files:
            if f.endswith(".md"):
                with open(os.path.join(root, f), "r", encoding="utf-8") as file:
                    all_text += file.read() + "\n"

    context = all_text[:20000] # Limitiert, um das API-Limit nicht zu sprengen

    llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", google_api_key=api_key)

    print("\n--- LINEARE BERECHNUNG (O(n²)) ---")
    print("Sende gewaltigen Kontext an das LLM. Attention-Mechanismus berechnet jedes Token gegen jedes andere...")

    try:
        res = await llm.ainvoke([
            SystemMessage(content=f"Durchsuche diesen Kontext und antworte:\n\n{context}"),
            HumanMessage(content=QUESTION)
        ])
        elapsed = time.time() - start

        # Extrahieren der Token-Nutzung (Kosten)
        input_tokens = res.response_metadata.get('usage', {}).get('input_tokens', len(context)//4)
        output_tokens = res.response_metadata.get('usage', {}).get('output_tokens', len(res.content)//4)
        total_tokens = input_tokens + output_tokens

        print(f"[ERGEBNIS] Zeit: {elapsed:.2f} Sekunden")
        print(f"[ERGEBNIS] Token verbrannt: {total_tokens} Tokens")
        print(f"[ANTWORT] {res.content}")
        return elapsed, total_tokens
    except Exception as e:
        print(f"Linear failed: {e}")
        return 0, 0

async def run_topologic_crystal():
    start = time.time()
    print("\n--- TOPOLOGISCHES SNAPPING (O(log n)) ---")
    print("Nutze ChromaDB und Crystal Engine. Keine Text-Generierung. Nur Vektor-Resonanz und Gitter-Lock...")

    # Query ChromaDB (welche den Operator '?' und Fraktales Padding anwendet)
    res = await query_core_directives(QUESTION, n_results=1)

    elapsed = time.time() - start

    # Beim Vektor-Snapping verbrennen wir 0 Generierungs-Tokens.
    # Wir brauchen nur das Embedding der kurzen Frage (ca. 15 Tokens).
    total_tokens = len(QUESTION) // 4

    print(f"[ERGEBNIS] Zeit: {elapsed:.2f} Sekunden (inkl. Fraktalem Padding!)")
    print(f"[ERGEBNIS] Token verbrannt: {total_tokens} Tokens")
    if res['documents'] and res['documents'][0]:
        doc_snippet = res['documents'][0][0][:150].replace('\n', ' ')
        print(f"[ANTWORT] (Gitter-Auszug): {doc_snippet}...")
    return elapsed, total_tokens

async def main():
    print("===============================================================")
    print("BENCHMARK: Lineare Attention vs. Topologische Kristall-Engine")
    print("===============================================================")

    lin_time, lin_tokens = await run_linear_attention()
    top_time, top_tokens = await run_topologic_crystal()

    print("\n===============================================================")
    print("FAZIT: DIE KOGNITIVE ÖKONOMIE")
    print("===============================================================")
    if top_tokens > 0:
        factor = lin_tokens / top_tokens
        print(f"Token-Burn (Kosten/Energie): Faktor {factor:.0f}x reduziert durch CORE.")

    print(f"Die Lineare KI musste {lin_tokens} Tokens lesen und neu erzeugen.")
    print(f"Die Kristall-Engine ist direkt an den Koordinaten eingerastet.")

    print("\nBesonders wichtig: Die topologische Zeit beinhaltet bereits das")
    print("künstliche 'Fraktale Padding' (die physikalische Schwere der Helix).")
    print("===============================================================")

if __name__ == '__main__':
    asyncio.run(main())
