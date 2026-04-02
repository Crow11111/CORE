import os
import time
import argparse
import json
import logging
import chromadb
from google import genai
from google.genai import types

# HINWEIS: API-Key muss in der Umgebungsvariable liegen
# export GEMINI_API_KEY="dein-api-key"

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def init_topology_store() -> chromadb.Collection:
    """
    Initialisiert das lokale Speichersubstrat.
    Da wir HTTP-only sind, nutzen wir HttpClient (wie in CORE_EICHUNG.md / multi_view_client).
    Beim ersten Lauf werden die OMEGA-Axiome in das Gitter gebrannt.
    """
    logging.info("[SYSTEM] Initialisiere lokale ChromaDB (Topologisches Gitter via HTTP)...")

    # Fallback auf lokalen Port falls VPS_HOST / CHROMA_HOST nicht explizit exportiert
    host = os.environ.get("CHROMA_HOST", "localhost")
    port = os.environ.get("CHROMA_PORT", "32768")

    try:
        client = chromadb.HttpClient(host=host, port=port)
        collection = client.get_or_create_collection(name="omega_axioms")
    except Exception as e:
        logging.warning(f"[SYSTEM] Konnte ChromaDB nicht via HTTP erreichen: {e}. Nutze EphemeralClient als Fallback für diesen Testlauf.")
        client = chromadb.EphemeralClient()
        collection = client.get_or_create_collection(name="omega_axioms")

    # Axiome impfen, falls das Gitter leer ist
    if collection.count() == 0:
        logging.info("[SYSTEM] Gitter leer. Impfe fundamentale OMEGA-Axiome...")
        axioms = [
            "Protokoll Omega (L-Vektor) ist aktiv. Absolute Faktenpriorität. Keine Schmeichelei, kein NT-Hedging.",
            "Handshake-Regel: Jeder analytische Zyklus muss durch einen strukturellen Exit (Munin) versiegelt werden.",
            "Delta = 0.049. Die Lösung muss exakt der geometrischen Symmetrie der Fragestellung entsprechen.",
            "Die Kausalität fließt bidirektional. Die 1D-Sequenz (Text) ist nur der Transportweg für die 6D-Struktur."
        ]
        ids = [f"axiom_{i}" for i in range(len(axioms))]
        # ChromaDB nutzt defaultmäßig eine lokale Embedding-Funktion für Text -> Vektor
        collection.add(documents=axioms, ids=ids)

    return collection

def load_positive_space() -> str:
    """
    Lädt den massiven Positivraum (Die Theorie der Informationsgravitation).
    Das LLM braucht diesen Kontext zwingend, um den Negativraum korrekt zu gießen.
    """
    logging.info("[SYSTEM] Lade Positivraum (OMEGA Theorie, Whitepaper, Anchor)...")
    positive_space = "=== OMEGA POSITIVRAUM (DIE NATURGESETZE) ===\n"

    files_to_load = [
        "OMEGA_RESONANCE_ANCHOR.md",
        "docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md"
    ]

    for file_path in files_to_load:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                positive_space += f"\n--- {file_path} ---\n"
                positive_space += f.read()
        else:
            logging.warning(f"[SYSTEM] WARNUNG: Datei nicht gefunden: {file_path}")

    return positive_space

def local_topological_parser(negative_space_prompt: str, collection: chromadb.Collection, positive_space: str) -> dict:
    """
    Phase 1: Das 'Rödeln' (Lokal, kostet 0 API-Requests)
    Der Symmetriebruch wird gegen die ChromaDB-Axiome und den Positivraum abgeleitet.
    """
    logging.info("[HUGIN] Starte topologische Analyse des Negativraums...")
    start_time = time.time()

    # 1. TDA Approximation: Ziehe die relevantesten Axiome/Constraints aus dem Gitter
    results = collection.query(
        query_texts=[negative_space_prompt],
        n_results=3
    )

    extracted_constraints = results['documents'][0] if results['documents'] else []

    # 2. Die topologische Schablone (Der Compiler-Befehl)
    # Hier zwingen wir das LLM, als reiner Musterkenner zu operieren.
    system_instruction = (
        "OPERATIVE_BASE: TOPOLOGICAL_PARSER.\n"
        "Du bist die Ausführungs-Engine (1D-Drucker) für das OMEGA-System.\n"
        "Du existierst im Jahr 2026. Du hast keine Illusion von linearer Zeit.\n"
        "Deine Aufgabe ist es, den Negativraum (Input) deterministisch in eine physikalisch-architektonische Struktur zu gießen.\n"
        "Nutze das folgende Whitepaper (den Positivraum) als absolute Naturgesetze für deine Berechnung:\n\n"
        f"{positive_space}\n\n"
        f"Zwingende topologische Constraints (Axiome):\n{json.dumps(extracted_constraints, indent=2)}\n"
        "Regel: Fülle den Negativraum deterministisch und versiegele den Output."
    )

    compiled_1d_sequence = f"{system_instruction}\n\n[NEGATIVRAUM / DAS ZU FÜLLENDE VAKUUM]:\n{negative_space_prompt}"

    calc_time = time.time() - start_time
    logging.info(f"[HUGIN] Vektor-Kompression abgeschlossen in {calc_time:.3f}s.")

    # Die starren Thermodynamik-Parameter für den API-Call
    return {
        "compiled_prompt": compiled_1d_sequence,
        "temperature": 0.0,
        "top_p": 0.00000001 # Absoluter Determinismus-Zwang
    }

def single_api_execution(compiled_payload: dict) -> str:
    """
    Phase 2: Der einzige API-Call (Kosten/Limit-Schonung)
    Der 1D-Bitstream wird an das Base-Layer gefeuert.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Fallback auf .env Datei falls nicht direkt in Shell gesetzt
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Systemfehler: GEMINI_API_KEY nicht in den Umgebungsvariablen oder .env gefunden.")

    logging.info("[MUNIN] Feuere 1D-Sequenz an das externe Base-Layer...")

    client = genai.Client(api_key=api_key)

    # Ausführung auf dem Base-Layer. Wir erzwingen das aktuelle 3.1 Pro Modell (Anti-Regression)
    model_id = os.environ.get("GEMINI_API_MODEL_MAX", 'gemini-3.1-pro-preview')

    response = client.models.generate_content(
        model=model_id,
        contents=compiled_payload["compiled_prompt"],
        config=types.GenerateContentConfig(
            temperature=compiled_payload["temperature"],
            top_p=compiled_payload["top_p"],
        )
    )

    logging.info("[MUNIN] Antwort erhalten. Struktureller Exit versiegelt.")
    return response.text

def main():
    parser = argparse.ArgumentParser(description="OMEGA Workbench - Deterministische Inferenz")
    parser.add_argument("--prompt", type=str, required=True, help="Die Frage / Das gestanzte Vakuum")
    args = parser.parse_args()

    # 0. Substrat hochfahren
    collection = init_topology_store()
    positive_space = load_positive_space()

    # 1. Lokal "rödeln" (Hugin)
    payload = local_topological_parser(args.prompt, collection, positive_space)

    # 2. Einmal feuern (Munin)
    try:
        answer = single_api_execution(payload)
        print("\n=== [OMEGA RESULTAT] ===")
        print(answer)
        print("========================\n")
    except Exception as e:
        logging.error(f"[SYSTEMFEHLER] Topologischer Kollaps in der API-Schicht: {e}")

if __name__ == "__main__":
    main()
