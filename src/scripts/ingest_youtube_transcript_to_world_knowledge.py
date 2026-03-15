# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# ============================================================
"""
Einmalig: YOUTUBE_TRANSCRIPT_GEMINI_RAG.md in ChromaDB world_knowledge einpflegen.
Chunking: Abschnitt -> Absatz -> Satz (wie ingest_mth_profile_to_chroma).
Metadata: source_file, category=rag_reference, optional chunk_index (Schema world_knowledge).
"""
from __future__ import annotations

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SOURCE_FILE = "YOUTUBE_TRANSCRIPT_GEMINI_RAG.md"
TRANSCRIPT_PATH = os.path.join(PROJECT_ROOT, "docs", "05_AUDIT_PLANNING", SOURCE_FILE)
MIN_CHUNK_LEN = 15
MAX_SENTENCE_JOIN = 3
MAX_SECTION_LEN = 12000


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if len(p.strip()) >= MIN_CHUNK_LEN]


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    out = []
    buf = []
    for p in parts:
        p = p.strip()
        if not p or len(p) < 10:
            continue
        buf.append(p)
        if len(buf) >= MAX_SENTENCE_JOIN or (buf and len(" ".join(buf)) > 280):
            out.append(" ".join(buf))
            buf = []
    if buf:
        out.append(" ".join(buf))
    return out if out else ([text] if len(text) >= MIN_CHUNK_LEN else [])


def chunk_multidepth(content: str) -> list[tuple[str, dict]]:
    """[(document_text, metadata)] mit source_file, category, optional chunk_index."""
    chunks = []
    # Tier 1: ganzer Inhalt (gekuerzt wenn zu lang)
    if len(content) > MAX_SECTION_LEN:
        tier1_text = content[:MAX_SECTION_LEN] + "\n[... gekuerzt ...]"
    else:
        tier1_text = content
    if len(tier1_text.strip()) >= MIN_CHUNK_LEN:
        chunks.append((tier1_text.strip(), {
            "source_file": SOURCE_FILE,
            "category": "rag_reference",
            "chunk_index": 0,
        }))

    # Tier 2: Absaetze
    for i, para in enumerate(_split_paragraphs(content)):
        if len(para) < 5000:
            chunks.append((para, {
                "source_file": SOURCE_FILE,
                "category": "rag_reference",
                "chunk_index": i,
            }))

    # Tier 3: Saetze / 2–3 Saetze
    for para in _split_paragraphs(content):
        for sent in _split_sentences(para):
            if len(sent) >= MIN_CHUNK_LEN:
                chunks.append((sent, {
                    "source_file": SOURCE_FILE,
                    "category": "rag_reference",
                }))

    return chunks


def main() -> int:
    if not os.path.isfile(TRANSCRIPT_PATH):
        print(f"[ingest_youtube_transcript] Datei nicht gefunden: {TRANSCRIPT_PATH}")
        return 1

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    # Fliesstext ab Zeile 3: erste Zeile = Titel, zweite leer, ab dritter Inhalt
    lines = raw.split("\n")
    if len(lines) >= 3:
        content = "\n".join(lines[2:]).strip()
    else:
        content = raw.strip()

    if not content or len(content) < MIN_CHUNK_LEN:
        print("[ingest_youtube_transcript] Kein ausreichender Inhalt.")
        return 1

    chunks = chunk_multidepth(content)
    if not chunks:
        print("[ingest_youtube_transcript] Keine Chunks erzeugt.")
        return 1

    from src.network.chroma_client import _get_collection_sync

    col = _get_collection_sync("world_knowledge", create_if_missing=True)
    ids = []
    documents = []
    metadatas = []

    for i, (text, meta) in enumerate(chunks):
        ids.append(f"yt_rag_{i}")
        documents.append(text)
        flat_meta: dict = {
            "source_file": str(meta.get("source_file", SOURCE_FILE))[:200],
            "category": str(meta.get("category", "rag_reference")),
            "chunk_index": i,
        }
        metadatas.append(flat_meta)

    col.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"[ingest_youtube_transcript] {len(ids)} Chunks in world_knowledge geschrieben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
