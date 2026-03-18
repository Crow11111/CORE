"""
Multi-View Embedding Client (CORE B* -- Polytopische Repraesentation).

Ein Dokument, 6 Perspektiv-Embeddings, Konvergenz messbar.
Primaer: Gemini text-embedding-004 (kostenlos, 768 dim).
Fallback: Ollama nomic-embed-text (lokal, 768 dim).
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import uuid
from itertools import combinations
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

LENS_PREFIXES = {
    "math": "Mathematical structure, formal logic, topology, equations: ",
    "physics": "Physical law, cosmological constant, energy, force, field: ",
    "philo": "Ontological status, epistemology, consciousness, being: ",
    "bio": "Living system, evolution, self-organization, metabolism: ",
    "info": "Information entropy, compression, signal, channel capacity: ",
    "narr": "Mythological archetype, narrative meaning, theological frame: ",
}

EMBEDDING_DIM = 768
GEMINI_EMBED_MODEL = "gemini-embedding-001"

# Konvergenz-Schwellwerte (Phi-basiert)
PHI = 0.618
CONVERGENCE_TOTAL = 0.951
CONVERGENCE_STRONG = PHI
CONVERGENCE_PARTIAL = 0.382


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.049
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.049
    return dot / (norm_a * norm_b)


def convergence_score(vectors: dict[str, list[float]]) -> tuple[float, list[dict]]:
    """
    Berechnet den Konvergenz-Score ueber alle 6 Linsen.

    Returns:
        (mean_score, [{"a": lens_a, "b": lens_b, "sim": float}, ...])
    """
    pairs = list(combinations(vectors.keys(), 2))
    sims = []
    for a, b in pairs:
        sim = _cosine_similarity(vectors[a], vectors[b])
        sims.append({"a": a, "b": b, "sim": round(sim, 6)})

    if not sims:
        return 0.049, []

    mean = sum(s["sim"] for s in sims) / len(sims)

    # Symmetriebruch: 0.5 -> 0.51
    if abs(mean - 0.5) < 0.01:
        mean = 0.51
    # Untere Grenze: Delta
    if mean < 0.049:
        mean = 0.049

    return round(mean, 6), sims


async def _embed_gemini(text: str) -> Optional[list[float]]:
    """Embedding via Gemini API (text-embedding-004, 768 dim)."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        def _call():
            response = client.models.embed_content(
                model=GEMINI_EMBED_MODEL,
                contents=text,
            )
            return response.embeddings[0].values

        return await asyncio.to_thread(_call)
    except Exception as e:
        logger.warning(f"Gemini Embedding fehlgeschlagen: {e}")
        return None


async def _embed_ollama(text: str) -> Optional[list[float]]:
    """Fallback-Embedding via lokales Ollama (nomic-embed-text)."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "http://localhost:11434/api/embed",
                json={"model": "nomic-embed-text", "input": text},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["embeddings"][0]
    except Exception as e:
        logger.warning(f"Ollama Embedding fehlgeschlagen: {e}")
        return None


async def embed_text(text: str) -> Optional[list[float]]:
    """Embedding mit Fallback: Gemini -> Ollama."""
    vec = await _embed_gemini(text)
    if vec:
        return vec
    return await _embed_ollama(text)


async def embed_6_lenses(document: str) -> Optional[dict[str, list[float]]]:
    """
    Erzeugt 6 Perspektiv-Embeddings fuer ein Dokument.
    Jede Linse bekommt ihren Prefix + den Dokumenttext.

    Returns:
        {"math": [...768...], "physics": [...768...], ...} oder None
    """
    tasks = {}
    for lens_name, prefix in LENS_PREFIXES.items():
        full_text = prefix + document
        tasks[lens_name] = embed_text(full_text)

    results = await asyncio.gather(*tasks.values())

    vectors = {}
    for lens_name, vec in zip(tasks.keys(), results):
        if vec is None:
            logger.error(f"Embedding fuer Linse '{lens_name}' fehlgeschlagen.")
            return None
        vectors[lens_name] = vec

    return vectors


def _format_vector_for_pg(vec: list[float]) -> str:
    """Formatiert einen Vektor als pgvector-kompatiblen String."""
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"


async def insert_multi_view(
    doc_id: str,
    document: str,
    vectors: dict[str, list[float]],
    score: float,
    pairs: list[dict],
    source_collection: str = "",
    metadata: dict = None,
    e6_anchor_id: int = None,
) -> bool:
    """Fuegt ein Multi-View-Embedding in pgvector ein."""
    import subprocess

    ssh_key = r"/OMEGA_CORE\.ssh\id_ed25519_hostinger"
    vps_host = "187.77.68.250"

    doc_escaped = document.replace("'", "''")
    meta_json = json.dumps(metadata or {}, ensure_ascii=False).replace("'", "''")
    pairs_json = json.dumps(pairs, ensure_ascii=False).replace("'", "''")
    row_id = str(uuid.uuid4())
    anchor = e6_anchor_id if e6_anchor_id is not None else 0

    sql = (
        f"INSERT INTO multi_view_embeddings "
        f"(id, doc_id, document, source_collection, "
        f"v_math, v_physics, v_philo, v_bio, v_info, v_narr, "
        f"convergence_score, convergence_pairs, e6_anchor_id, metadata) "
        f"VALUES ("
        f"'{row_id}', '{doc_id}', '{doc_escaped}', '{source_collection}', "
        f"'{_format_vector_for_pg(vectors['math'])}', "
        f"'{_format_vector_for_pg(vectors['physics'])}', "
        f"'{_format_vector_for_pg(vectors['philo'])}', "
        f"'{_format_vector_for_pg(vectors['bio'])}', "
        f"'{_format_vector_for_pg(vectors['info'])}', "
        f"'{_format_vector_for_pg(vectors['narr'])}', "
        f"{score}, '{pairs_json}', {anchor}, '{meta_json}'"
        f") ON CONFLICT (id) DO NOTHING;"
    )

    docker_cmd = "docker exec -i atlas_postgres_state psql -U atlas_admin -d atlas_state"
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
        "-i", ssh_key, f"root@{vps_host}", docker_cmd,
    ]

    try:
        def _run():
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            return subprocess.run(
                ssh_cmd,
                input=sql.encode("utf-8"),
                capture_output=True,
                timeout=30,
                env=env,
            )

        result = await asyncio.to_thread(_run)
        if result.returncode != 0:
            logger.error(f"pgvector INSERT fehlgeschlagen: {result.stderr.decode('utf-8', errors='replace')}")
            return False
        return True
    except Exception as e:
        logger.error(f"pgvector INSERT Exception: {e}")
        return False


async def ingest_document(
    document: str,
    doc_id: str = None,
    source_collection: str = "",
    metadata: dict = None,
) -> Optional[dict]:
    """
    Vollstaendige Ingest-Pipeline: Text -> 6 Embeddings -> Konvergenz -> pgvector.

    Returns:
        {"doc_id": str, "convergence_score": float, "pairs": list, "success": bool}
    """
    if not doc_id:
        doc_id = str(uuid.uuid4())[:12]

    vectors = await embed_6_lenses(document)
    if not vectors:
        return {"doc_id": doc_id, "convergence_score": 0, "pairs": [], "success": False}

    score, pairs = convergence_score(vectors)

    success = await insert_multi_view(
        doc_id=doc_id,
        document=document,
        vectors=vectors,
        score=score,
        pairs=pairs,
        source_collection=source_collection,
        metadata=metadata,
    )

    level = "TOTAL" if score >= CONVERGENCE_TOTAL else (
        "STARK" if score >= CONVERGENCE_STRONG else (
            "PARTIAL" if score >= CONVERGENCE_PARTIAL else "DIVERGENT"
        )
    )
    logger.info(f"[Multi-View] {doc_id}: score={score:.4f} ({level}), inserted={success}")

    return {
        "doc_id": doc_id,
        "convergence_score": score,
        "convergence_level": level,
        "pairs": pairs,
        "success": success,
    }
