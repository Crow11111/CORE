"""
Batch-Ingest: CORE Kern-Dokumente durch die 6-Linsen Multi-View Pipeline.

Chunkt Gemini-Dialoge an natuerlichen Grenzen (Sprecher-Wechsel),
embedded jeden Chunk durch 6 Perspektiven, berechnet Konvergenz,
speichert in pgvector.

Gemini embedding API: 1500 RPM (Free Tier), 6 calls pro Chunk.
Bei ~250 Chunks/Datei und 6 Linsen = 1500 calls -> passt in 1 Minute.
Wir throttlen vorsichtig mit 0.3s zwischen Chunks.
"""
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

import asyncio
import re
import time
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.db.multi_view_client import ingest_document


CHUNK_MIN_CHARS = 200
CHUNK_MAX_CHARS = 3000
DELAY_BETWEEN_CHUNKS = 0.5

DIALOG_MARKERS = [
    r"^Du hast gesagt$",
    r"^Gemini hat gesagt$",
    r"^ATLAS aktiv\.",
    r"^---$",
    r"^## Eintrag \d+",
]
MARKER_PATTERN = re.compile("|".join(DIALOG_MARKERS), re.MULTILINE)


def chunk_dialog(text: str, source: str) -> list[dict]:
    """Zerlegt Gemini-Dialoge an Sprecher-Wechseln."""
    splits = MARKER_PATTERN.split(text)
    marker_matches = MARKER_PATTERN.findall(text)

    chunks = []
    current = ""
    current_speaker = "unknown"

    for i, block in enumerate(splits):
        block = block.strip()
        if not block:
            continue

        if i > 0 and i - 1 < len(marker_matches):
            marker = marker_matches[i - 1].strip()
            if "Du hast gesagt" in marker:
                current_speaker = "marc"
            elif "Gemini hat gesagt" in marker or "ATLAS aktiv" in marker:
                current_speaker = "gemini"
            elif "Eintrag" in marker:
                current_speaker = "entry"

        if len(current) + len(block) > CHUNK_MAX_CHARS and len(current) >= CHUNK_MIN_CHARS:
            chunk_id = hashlib.md5(current[:100].encode()).hexdigest()[:12]
            chunks.append({
                "text": current.strip(),
                "doc_id": f"{source}_{chunk_id}",
                "speaker": current_speaker,
                "source": source,
            })
            current = block
        else:
            current += "\n\n" + block if current else block

    if current.strip() and len(current.strip()) >= CHUNK_MIN_CHARS:
        chunk_id = hashlib.md5(current[:100].encode()).hexdigest()[:12]
        chunks.append({
            "text": current.strip(),
            "doc_id": f"{source}_{chunk_id}",
            "speaker": current_speaker,
            "source": source,
        })

    return chunks


def chunk_plain(text: str, source: str) -> list[dict]:
    """Fallback-Chunker fuer nicht-dialogische Texte."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) > CHUNK_MAX_CHARS and len(current) >= CHUNK_MIN_CHARS:
            chunk_id = hashlib.md5(current[:100].encode()).hexdigest()[:12]
            chunks.append({
                "text": current.strip(),
                "doc_id": f"{source}_{chunk_id}",
                "speaker": "mixed",
                "source": source,
            })
            current = para
        else:
            current += "\n\n" + para if current else para

    if current.strip() and len(current.strip()) >= CHUNK_MIN_CHARS:
        chunk_id = hashlib.md5(current[:100].encode()).hexdigest()[:12]
        chunks.append({
            "text": current.strip(),
            "doc_id": f"{source}_{chunk_id}",
            "speaker": "mixed",
            "source": source,
        })

    return chunks


async def ingest_file(filepath: str, collection_name: str):
    """Liest eine Datei, chunked, embedded, speichert."""
    print(f"\n{'='*60}")
    print(f"INGEST: {filepath}")
    print(f"Collection: {collection_name}")
    print(f"{'='*60}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"Dateigroesse: {len(text):,} Zeichen")

    has_dialog = bool(MARKER_PATTERN.search(text))
    if has_dialog:
        chunks = chunk_dialog(text, collection_name)
        print(f"Chunking: Dialog-Modus ({len(chunks)} Chunks)")
    else:
        chunks = chunk_plain(text, collection_name)
        print(f"Chunking: Plain-Modus ({len(chunks)} Chunks)")

    total = len(chunks)
    success = 0
    failed = 0
    high_conv = []

    for i, chunk in enumerate(chunks):
        t0 = time.time()
        try:
            result = await ingest_document(
                document=chunk["text"],
                doc_id=chunk["doc_id"],
                source_collection=collection_name,
                metadata={"speaker": chunk["speaker"], "source_file": filepath},
            )

            elapsed = time.time() - t0
            score = result.get("convergence_score", 0)
            level = result.get("convergence_level", "?")
            ok = result.get("success", False)

            status = "OK" if ok else "FAIL"
            if ok:
                success += 1
            else:
                failed += 1

            if score >= 0.618:
                high_conv.append((chunk["doc_id"], score, level, chunk["text"][:80]))

            print(f"  [{i+1}/{total}] {status} | {chunk['doc_id'][:20]:20s} | "
                  f"conv={score:.4f} ({level:8s}) | {elapsed:.1f}s")

        except Exception as e:
            failed += 1
            print(f"  [{i+1}/{total}] ERROR | {chunk['doc_id'][:20]:20s} | {e}")

        if i < total - 1:
            await asyncio.sleep(DELAY_BETWEEN_CHUNKS)

    print(f"\n--- ERGEBNIS {collection_name} ---")
    print(f"Total: {total} | Erfolg: {success} | Fehler: {failed}")
    print(f"Hohe Konvergenz (>= Phi): {len(high_conv)}")
    for doc_id, score, level, preview in sorted(high_conv, key=lambda x: -x[1]):
        print(f"  {score:.4f} ({level}) | {doc_id} | {preview}...")
    print()

    return {"total": total, "success": success, "failed": failed, "high_convergence": high_conv}


async def main():
    files = [
        (r"c:\CORE\src\core\Leidensdruck und Genese.md", "core_genese"),
        (r"c:\CORE\Untitled-1.sty", "core_fraktal_dialog"),
    ]

    all_results = {}
    grand_high = []

    for filepath, collection in files:
        if not os.path.isfile(filepath):
            print(f"SKIP: {filepath} nicht gefunden")
            continue
        result = await ingest_file(filepath, collection)
        all_results[collection] = result
        grand_high.extend(result["high_convergence"])

    print("\n" + "=" * 60)
    print("GESAMT-KONVERGENZ-REPORT")
    print("=" * 60)
    total_chunks = sum(r["total"] for r in all_results.values())
    total_ok = sum(r["success"] for r in all_results.values())
    total_high = len(grand_high)
    print(f"Dateien: {len(all_results)} | Chunks: {total_chunks} | Erfolgreich: {total_ok}")
    print(f"Hohe Konvergenz (>= Phi=0.618): {total_high}")
    if grand_high:
        print(f"\nTop-10 Konvergenz-Punkte:")
        for doc_id, score, level, preview in sorted(grand_high, key=lambda x: -x[1])[:10]:
            print(f"  {score:.4f} ({level:8s}) | {doc_id}")
            print(f"    {preview}...")


if __name__ == "__main__":
    asyncio.run(main())
