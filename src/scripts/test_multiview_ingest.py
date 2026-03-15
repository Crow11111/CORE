"""Erster Test der Multi-View 6-Linsen-Pipeline."""
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
load_dotenv("c:/CORE/.env")


TEST_DOCS = [
    {
        "doc_id": "test_apoptose_001",
        "text": (
            "Apoptose ist der programmierte Zelltod. Das System zerstoert sich selbst, "
            "um das Ganze zu erhalten. In der Kosmologie entspricht dies dem baryonischen "
            "Delta von 0.049 -- dem Punkt, an dem Materie fast verschwindet, aber gerade "
            "genug uebrigbleibt, um Struktur zu bilden. In der Informationstheorie ist es "
            "der Moment maximaler Kompression: minimale Redundanz, maximale Bedeutung."
        ),
        "source": "test",
    },
    {
        "doc_id": "test_fibonacci_002",
        "text": (
            "Die Fibonacci-Sequenz und der Goldene Schnitt (Phi = 0.618) tauchen in "
            "Spiralgalaxien, DNA-Helices, Blattstellungen und Kristallgittern auf. "
            "Phi teilt jedes Intervall so, dass das Verhaeltnis des Ganzen zum Groesseren "
            "gleich dem des Groesseren zum Kleineren ist. Diese Selbstaehnlichkeit ist "
            "die Grundlage fraktaler Geometrie und erscheint in der Musik als harmonische "
            "Proportionen, in der Architektur als aesthetische Grundregel."
        ),
        "source": "test",
    },
]


async def main():
    from src.db.multi_view_client import ingest_document

    for doc in TEST_DOCS:
        print(f"\n{'='*60}")
        print(f"Ingest: {doc['doc_id']}")
        print(f"Text: {doc['text'][:80]}...")
        result = await ingest_document(
            document=doc["text"],
            doc_id=doc["doc_id"],
            source_collection=doc["source"],
        )
        print(f"Score:  {result['convergence_score']:.4f} ({result['convergence_level']})")
        print(f"Insert: {'OK' if result['success'] else 'FAILED'}")

        top_pairs = sorted(result["pairs"], key=lambda p: p["sim"], reverse=True)[:3]
        print("Top-3 Konvergenz-Paare:")
        for p in top_pairs:
            print(f"  {p['a']:8s} <-> {p['b']:8s}  sim={p['sim']:.4f}")

        bottom_pairs = sorted(result["pairs"], key=lambda p: p["sim"])[:2]
        print("Divergenteste Paare:")
        for p in bottom_pairs:
            print(f"  {p['a']:8s} <-> {p['b']:8s}  sim={p['sim']:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
