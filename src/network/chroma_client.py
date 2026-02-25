"""
ChromaDB-Client für ATLAS_CORE (lokal oder remote auf VPS).
Liest Konfiguration aus .env; bei CHROMA_HOST → HttpClient (VPS), sonst PersistentClient (lokal).
Collections laut Schnittstelle: argos_knowledge_graph, core_brain_registr, krypto_scan_buffer.
"""
import os
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

# Remote (VPS): CHROMA_HOST + CHROMA_PORT (Standard 8000)
CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip()
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
# Lokal (Dreadnought/Windows), wenn CHROMA_HOST leer
CHROMA_LOCAL_PATH = os.getenv("CHROMA_LOCAL_PATH", r"c:\ATLAS_CORE\data\chroma_db")

# Collection-Namen laut 03_DATENBANK_VECTOR_STORE_OSMIUM.md
COLLECTION_ARGOS = "argos_knowledge_graph"
COLLECTION_CORE_BRAIN = "core_brain_registr"
COLLECTION_KRYTO_SCAN = "krypto_scan_buffer"


def get_chroma_client():
    """Liefert ChromaDB-Client: HttpClient bei CHROMA_HOST, sonst PersistentClient lokal."""
    try:
        import chromadb
    except ImportError:
        raise ImportError("chromadb nicht installiert: pip install chromadb")

    if CHROMA_HOST:
        return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    if not os.path.exists(CHROMA_LOCAL_PATH):
        os.makedirs(CHROMA_LOCAL_PATH)
    return chromadb.PersistentClient(path=CHROMA_LOCAL_PATH)


def get_collection(name: str = COLLECTION_ARGOS, create_if_missing: bool = True):
    """Holt die angegebene Collection (Standard: argos_knowledge_graph)."""
    client = get_chroma_client()
    if create_if_missing:
        return client.get_or_create_collection(
            name=name,
            metadata={"description": f"ATLAS_CORE Collection: {name}"},
        )
    return client.get_collection(name=name)


def is_remote() -> bool:
    """True, wenn ChromaDB auf VPS (CHROMA_HOST) genutzt wird."""
    return bool(CHROMA_HOST)


def is_configured() -> bool:
    """True, wenn ChromaDB nutzbar ist (CHROMA_HOST gesetzt oder lokaler Pfad konfigurierbar)."""
    return bool(CHROMA_HOST) or bool(CHROMA_LOCAL_PATH)
