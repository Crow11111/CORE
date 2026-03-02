"""
Seed ATLAS Knowledge Base aus atlas_knowledge_chromadb_import.json in ChromaDB.

Importiert alle Kerninformationen (Identität, Architektur, Personen, Geräte, Integrationen)
in argos_knowledge_graph.

Usage:
    python -m src.scripts.seed_atlas_knowledge_base
    python -m src.scripts.seed_atlas_knowledge_base --dry-run
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.network.chroma_client import get_collection, COLLECTION_ARGOS


def _load_json():
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "knowledge_base", "atlas_knowledge_chromadb_import.json"
    )
    if not os.path.exists(path):
        path = r"c:\ATLAS_CORE\data\knowledge_base\atlas_knowledge_chromadb_import.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _metadata_sanitize(m: dict) -> dict:
    """ChromaDB erlaubt nur str, int, float, bool in metadata."""
    out = {}
    for k, v in m.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


def main():
    dry_run = "--dry-run" in sys.argv
    data = _load_json()
    docs = data.get("documents", [])
    if not docs:
        print("[WARN] Keine documents in JSON gefunden.")
        return

    if dry_run:
        print(f"[DRY-RUN] Würde {len(docs)} KB-Docs in argos_knowledge_graph importieren.")
        for d in docs[:8]:
            print(f"  - {d['id']} ({d['metadata'].get('category','?')})")
        if len(docs) > 8:
            print(f"  ... und {len(docs)-8} weitere")
        return

    col = get_collection(COLLECTION_ARGOS, create_if_missing=True)
    ids = [d["id"] for d in docs]
    documents = [d["document"] for d in docs]
    metadatas = [_metadata_sanitize(d.get("metadata", {})) for d in docs]
    try:
        col.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f"[OK] {len(docs)} KB-Dokumente in argos_knowledge_graph")
    except Exception as e:
        print(f"[FAIL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
