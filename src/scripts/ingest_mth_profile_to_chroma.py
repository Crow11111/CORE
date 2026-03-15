# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================
"""
MTH-Operator-Profil in ChromaDB (Collection mth_user_profile).
Tiefen-Chunking: Tier 1 = Abschnitt, Tier 2 = Absatz, Tier 3 = Satz/Phrase.
Trainingsdaten so tief wie möglich für RAG/OC Brain.
"""
from __future__ import annotations

import os
import re
import asyncio
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from loguru import logger

from src.network.chroma_client import (
    get_collection,
    COLLECTION_MTH_USER_PROFILE,
    is_remote,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))

# Quellen: (relativer Pfad ab PROJECT_ROOT, Kategorie, Slug)
SOURCES = [
    ("initailfunke.md", "meta_system", "initailfunke"),
    ("Untitled-1.sty", "session_insight", "untitled1"),
    ("docs/01_CORE_DNA/PROMPT_A_USER_PERSONA.md", "communication_style", "persona"),
    ("docs/01_CORE_DNA/RUECKWAERTSEVOLUTION.md", "cognitive_structure", "rueckwaertsevolution"),
    ("docs/01_CORE_DNA/nd_insights/01_ND_FAKTEN_FINAL.md", "cognitive_structure", "nd_fakten"),
    ("docs/01_CORE_DNA/nd_insights/02_ND_ANNAHMEN_FINAL.md", "cognitive_structure", "nd_annahmen"),
    ("docs/01_CORE_DNA/nd_insights_v4/CORE_ND_PROFILE_GOLD.md", "character", "nd_profile_gold"),
    ("docs/01_CORE_DNA/nd_insights_v4/CORE_REWE_AUDIO_ANALYSIS.md", "session_insight", "rewe_audio"),
    ("docs/01_CORE_DNA/nd_insights_full/01_ND_FAKTEN_VOLLSTAENDIG.md", "cognitive_structure", "nd_fakten_full"),
    ("docs/01_CORE_DNA/nd_insights_full/02_ND_ANNAHMEN_VOLLSTAENDIG.md", "cognitive_structure", "nd_annahmen_full"),
    ("docs/02_ARCHITECTURE/Initalfunke.md", "meta_system", "initalfunke_arch"),
]

# gemini.md separat (riesig): erste N Einträge
GEMINI_MD_PATH = os.path.join(PROJECT_ROOT, "gemini.md")
GEMINI_MAX_ENTRIES = 120
GEMINI_CATEGORY = "session_insight"
GEMINI_SLUG = "gemini"

MIN_CHUNK_LEN = 15
MAX_SENTENCE_JOIN = 3


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", s.lower())[:48]


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if len(p.strip()) >= MIN_CHUNK_LEN]


def _split_sentences(text: str) -> list[str]:
    # Grob: an . ! ? \n splitten, Leerzeichen trimmen
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


def chunk_multidepth(content: str, source_slug: str, category: str, source_file: str) -> list[tuple[str, dict]]:
    """Liefert [(document_text, metadata), ...] mit depth_tier 1, 2, 3."""
    chunks = []
    # Tier 1: ganzer Inhalt (gekürzt wenn zu lang)
    if len(content) > 12000:
        tier1_text = content[:12000] + "\n[... gekürzt ...]"
    else:
        tier1_text = content
    if len(tier1_text.strip()) >= MIN_CHUNK_LEN:
        chunks.append((tier1_text.strip(), {
            "source_file": source_file,
            "category": category,
            "depth_tier": 1,
            "source_slug": source_slug,
        }))

    # Tier 2: Absätze
    for i, para in enumerate(_split_paragraphs(content)):
        if len(para) < 5000:  # ein Absatz nicht wieder kürzen
            chunks.append((para, {
                "source_file": source_file,
                "category": category,
                "depth_tier": 2,
                "source_slug": source_slug,
                "chunk_index": i,
            }))

    # Tier 3: Sätze / 2–3 Sätze
    for para in _split_paragraphs(content):
        for sent in _split_sentences(para):
            if len(sent) >= MIN_CHUNK_LEN:
                chunks.append((sent, {
                    "source_file": source_file,
                    "category": category,
                    "depth_tier": 3,
                    "source_slug": source_slug,
                }))

    return chunks


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _parse_gemini_entries(path: str, max_entries: int) -> list[tuple[str, str]]:
    """Liest gemini.md und liefert [(entry_id, full_text), ...] für die ersten max_entries Einträge."""
    if not os.path.isfile(path):
        return []
    entries = []
    current = []
    current_id = None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.match(r"^## Eintrag (\d+)\s*$", line.strip())
            if m:
                if current_id is not None and current:
                    entries.append((f"eintrag_{current_id}", "\n".join(current)))
                    if len(entries) >= max_entries:
                        return entries
                current_id = int(m.group(1))
                current = [line]
            else:
                current.append(line)
        if current_id is not None and current:
            entries.append((f"eintrag_{current_id}", "\n".join(current)))
    return entries


async def _add_chunks_to_collection(collection, chunks: list[tuple[str, dict]], source_slug: str):
    if not chunks:
        return 0
    ids = []
    docs = []
    metadatas = []
    for i, (text, meta) in enumerate(chunks):
        # Chroma erlaubt nur str, int, float, bool in metadata
        flat_meta = {
            "source_file": str(meta.get("source_file", ""))[:200],
            "category": str(meta.get("category", "")),
            "depth_tier": int(meta.get("depth_tier", 2)),
            "source_slug": str(meta.get("source_slug", "")),
        }
        if "chunk_index" in meta:
            flat_meta["chunk_index"] = int(meta["chunk_index"])
        ids.append(f"{source_slug}_{meta.get('depth_tier', 2)}_{i}")
        docs.append(text)
        metadatas.append(flat_meta)

    # Chroma add (sync) – Embedding wird default generiert wenn nicht übergeben
    await asyncio.to_thread(collection.add, ids=ids, documents=docs, metadatas=metadatas)
    return len(ids)


async def ingest_single_file(
    collection,
    rel_path: str,
    category: str,
    source_slug: str,
) -> int:
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.isfile(full_path):
        logger.warning(f"Datei nicht gefunden: {full_path}")
        return 0
    content = await asyncio.to_thread(_read_file, full_path)
    file_name = os.path.basename(rel_path)
    chunks = chunk_multidepth(content, source_slug, category, file_name)
    n = await _add_chunks_to_collection(collection, chunks, source_slug)
    logger.info(f"{rel_path}: {len(chunks)} Chunks (Tiefen 1–3) -> {n} Vektoren")
    return n


async def ingest_gemini(collection) -> int:
    if not os.path.isfile(GEMINI_MD_PATH):
        logger.warning(f"gemini.md nicht gefunden: {GEMINI_MD_PATH}")
        return 0
    entries = await asyncio.to_thread(_parse_gemini_entries, GEMINI_MD_PATH, GEMINI_MAX_ENTRIES)
    total = 0
    for eid, text in entries:
        chunks = chunk_multidepth(text, GEMINI_SLUG, GEMINI_CATEGORY, "gemini.md")
        for _, meta in enumerate(chunks):
            meta["source_slug"] = f"{GEMINI_SLUG}_{eid}"
        n = await _add_chunks_to_collection(collection, chunks, f"{GEMINI_SLUG}_{eid}")
        total += n
    logger.info(f"gemini.md: {len(entries)} Einträge -> {total} Vektoren")
    return total


async def main():
    logger.info("Verbinde zu ChromaDB (mth_user_profile)...")
    col = await get_collection(COLLECTION_MTH_USER_PROFILE, create_if_missing=True)
    logger.info(f"Collection {COLLECTION_MTH_USER_PROFILE} bereit (remote={is_remote()}).")

    total = 0
    for rel_path, category, slug in SOURCES:
        n = await ingest_single_file(col, rel_path, category, slug)
        total += n

    total += await ingest_gemini(col)

    logger.success(f"MTH-Profil: insgesamt {total} Chunks in {COLLECTION_MTH_USER_PROFILE}.")
    return total


if __name__ == "__main__":
    import os as _os
    _os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main())
