"""
Multi-View Embedding Client (CORE B* -- Polytopische Repraesentation).

Eskalationspyramide:
  Stufe 1 (lokal):  embed_local() -> Ollama nomic-embed-text (768 dim, 0 Kosten)
                    Fuer Routing, Similarity, Triage, Gravitator.
  Stufe 2 (API):    embed_text()  -> Gemini Embedding 2 (3072 dim, API-Kosten)
                    Fuer 6-Linsen Multi-View Persistenz in pgvector.
  Stufe 3 (multi):  embed_multimodal() -> Gemini Embedding 2 (3072 dim, Bild/Audio/Video/PDF)
                    Nativ multimodal, selber Vektorraum wie Text.

Duale Topologie:
  ChromaDB  = Routing-Cache (Gravitator)
  pgvector  = Deep Persistenz (Multi-View Embeddings, v_multimodal)
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import re
import uuid
from itertools import combinations
from typing import Optional, Union

from dotenv import load_dotenv
from loguru import logger

from src.network import chroma_client

load_dotenv()

LENS_PREFIXES = {
    "math": "Mathematical structure, formal logic, topology, equations: ",
    "physics": "Physical law, cosmological constant, energy, force, field: ",
    "philo": "Ontological status, epistemology, consciousness, being: ",
    "bio": "Living system, evolution, self-organization, metabolism: ",
    "info": "Information entropy, compression, signal, channel capacity: ",
    "narr": "Mythological archetype, narrative meaning, theological frame: ",
}

# --- AI CONTEXT SEPARATION ---
# AI-Generated Content Collections (Stufe 2 der Dualen Topologie)
COLLECTION_AI_MV_KEYWORDS = "ai_mv_keywords"
COLLECTION_AI_MV_SEMANTICS = "ai_mv_semantics"
COLLECTION_AI_MV_MEDIA = "ai_mv_media"

AI_FACET_TO_COLLECTION = {
    "keywords": COLLECTION_AI_MV_KEYWORDS,
    "semantics": COLLECTION_AI_MV_SEMANTICS,
    "media_descriptors": COLLECTION_AI_MV_MEDIA,
}

# Standard-Vertrauens-Level (Axiom A5/Baryonic Delta)
TRUST_AI = 0.049    # Skeptische Grundhaltung für KI-Kontext
TRUST_USER = 0.951  # Hoher Vertrauensanker für Operator-Daten

# Konvergenz-Schwellwerte (Phi-basiert)
PHI = 0.618
CONVERGENCE_TOTAL = 0.951
CONVERGENCE_STRONG = PHI
CONVERGENCE_PARTIAL = 0.382

# --- KARDANISCHE FALTUNG (Complex -> 2x Float) ---
def _fold_complex(val: Union[float, complex, list[float], list[complex]]) -> list[float]:
    """Faltet komplexe Werte in zwei reine float-Werte (Real- und Imaginärteil)."""
    if isinstance(val, (float, int)):
        return [float(val), 0.0]
    if isinstance(val, complex):
        return [val.real, val.imag]
    if isinstance(val, list):
        folded = []
        for v in val:
            if isinstance(v, complex):
                folded.extend([v.real, v.imag])
            else:
                folded.extend([float(v), 0.0])
        return folded
    return [0.0, 0.0]

# --- ATLAS HARDENING ---
HARDENING_THRESHOLD = PHI # Schwellwert für Atlas-gehärtete Signale (0.618)

def _is_atlas_hardened(score: Union[float, complex]) -> bool:
    """Prüft ob ein Signal die Atlas-Härtungsschwelle erreicht (Magnitude)."""
    return abs(score) >= HARDENING_THRESHOLD

# --- 3 DYNAMISCHE FACETTEN (Keywords, Semantics, Media Descriptors) ---
# Asynchrone Entkopplung: Die neuen Facetten ersetzen kuenftig die 6 starren Linsen.
# Sie werden in isolierten Vektor-Raeumen (ChromaDB Collections) gespeichert.
FACET_PREFIXES = {
    "keywords": "Extract exact keywords, domain terminology, core entities, and literal identifiers: ",
    "semantics": "Analyze underlying meaning, contextual intent, abstract concepts, and latent relationships: ",
    "media_descriptors": "Describe modal properties, structural format, visual/auditory characteristics, and stylistic traits: ",
}

# ChromaDB Collections fuer isolierte Raeume (float-Kern)
COLLECTION_MV_KEYWORDS = "mv_keywords"
COLLECTION_MV_SEMANTICS = "mv_semantics"
COLLECTION_MV_MEDIA = "mv_media"

FACET_TO_COLLECTION = {
    "keywords": COLLECTION_MV_KEYWORDS,
    "semantics": COLLECTION_MV_SEMANTICS,
    "media_descriptors": COLLECTION_MV_MEDIA,
}

# Gemini text-embedding / aktuelle API: typisch 3072 (Legacy 768 — Tabelle muss passen)
EMBEDDING_DIM_768 = 768
EMBEDDING_DIM_3072 = 3072
EMBEDDING_DIM = EMBEDDING_DIM_3072  # Standard fuer Deep (Stufe 2)


def _gemini_embed_model() -> str:
    """RAG-Vektorisierung: Modell aus Registry (GEMINI_EMBED_MODEL)."""
    from src.ai.model_registry import get_model_for_role
    return (get_model_for_role("embedding") or "gemini-embedding-001").strip()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.049
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.049
    return dot / (norm_a * norm_b)


def convergence_score(vectors: dict[str, list[float]] | dict[str, dict[str, list[float]]]) -> tuple[float, list[dict]]:
    """
    Berechnet den Konvergenz-Score ueber alle 6 Linsen.
    Nutzt standardmaessig die 3072-dim Vektoren (Deep Resonance) falls vorhanden.

    Returns:
        (mean_score, [{"a": lens_a, "b": lens_b, "sim": float}, ...])
    """
    # Funnel-Support: Extrahiere Deep Vektoren (3072) falls dual vorliegend
    active_vectors = {}
    for k, v in vectors.items():
        if isinstance(v, dict) and "3072" in v:
            active_vectors[k] = v["3072"]
        elif isinstance(v, dict) and "768" in v:
            active_vectors[k] = v["768"]
        else:
            active_vectors[k] = v

    pairs = list(combinations(active_vectors.keys(), 2))
    sims = []
    for a, b in pairs:
        sim = _cosine_similarity(active_vectors[a], active_vectors[b])
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
    """Embedding via Gemini Embedding 2 API (3072 dim). Kosten: API-Call."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    model = _gemini_embed_model()
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        def _call():
            response = client.models.embed_content(
                model=model,
                contents=text
            )
            return response.embeddings[0].values

        return await asyncio.wait_for(asyncio.to_thread(_call), timeout=15.0)
    except asyncio.TimeoutError:
        logger.warning(f"Gemini Embedding ({model}) Timeout nach 15s.")
        return None
    except Exception as e:
        logger.warning(f"Gemini Embedding ({model}) fehlgeschlagen: {e}")
        return None


OLLAMA_EMBED_HOST = os.getenv("OLLAMA_EMBED_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")


async def _embed_ollama(text: str) -> Optional[list[float]]:
    """Embedding via Ollama nomic-embed-text (768 dim). Kosten: 0.
    Wird auf dem OC Brain (VPS) via Tunnel ausgefuehrt, Dreadnought orchestriert nur.
    """
    try:
        import httpx
        logger.debug(f"Ollama Call to {OLLAMA_EMBED_HOST}/api/embed with model {OLLAMA_EMBED_MODEL}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{OLLAMA_EMBED_HOST}/api/embed",
                json={"model": OLLAMA_EMBED_MODEL, "input": text},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["embeddings"][0]
    except Exception as e:
        logger.warning(f"Ollama Embedding ({OLLAMA_EMBED_MODEL}) fehlgeschlagen: {e}")
        return None


async def embed_local(text: str) -> Optional[list[float]]:
    """Stufe 1: Routing Embedding via OC Brain (768 dim, 0 Kosten, ~50ms).

    Fuer Routing, Similarity-Checks, Triage, Gravitator. Laeuft auf dem VPS.
    Fallback auf Gemini wenn VPS/Ollama nicht erreichbar.
    """
    vec = await _embed_ollama(text)
    if vec:
        return vec
    return await _embed_gemini(text)


async def embed_text(text: str) -> Optional[list[float]]:
    """Stufe 2: Deep Embedding (3072 dim, API-Kosten).

    Fuer Multi-View Persistenz in pgvector (3 Facetten).
    Fallback auf VPS/Ollama wenn API nicht erreichbar.
    """
    vec = await _embed_gemini(text)
    if vec:
        return vec
    return await _embed_ollama(text)


async def embed_multimodal(
    file_path: str,
    mime_type: str,
    text_context: str = "",
) -> Optional[list[float]]:
    """Multimodales Embedding via Gemini Embedding 2 (Bild/Audio/Video/PDF).

    Mappt beliebige Medien in denselben 3072-dim Vektorraum wie Text.
    Optional mit Text-Kontext für interleaved Embedding.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    model = _gemini_embed_model()
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        def _call():
            uploaded = client.files.upload(file=file_path)
            try:
                parts = [types.Part.from_uri(file_uri=uploaded.uri, mime_type=mime_type)]
                if text_context:
                    parts.insert(0, types.Part.from_text(text=text_context))

                response = client.models.embed_content(
                    model=model,
                    contents=types.Content(parts=parts),
                )
                return response.embeddings[0].values
            finally:
                try:
                    client.files.delete(name=uploaded.name)
                except Exception:
                    pass

        return await asyncio.to_thread(_call)
    except Exception as e:
        logger.warning(f"Multimodal Embedding ({model}) fehlgeschlagen: {e}")
        return None


async def embed_3_facets(document: str) -> Optional[dict[str, dict[str, list[float]]]]:
    """
    Erzeugt 3 Facetten-Embeddings fuer ein Dokument (Keywords, Semantics, Media Descriptors).
    Asynchrone Entkopplung: Die Generierung der 3 Facetten x 2 Dimensionen erfolgt parallel.

    Returns:
        {"keywords": {"768": [...], "3072": [...]}, ...} oder None
    """
    # 0. Bias Damper (Clean-up before vectorization)
    document = _apply_bias_damper(document)

    tasks_768 = {}
    tasks_3072 = {}
    for facet_name, prefix in FACET_PREFIXES.items():
        full_text = prefix + document
        # Parallel fuer 3 Facetten x 2 Dimensionen
        tasks_768[facet_name] = _embed_ollama(full_text)
        tasks_3072[facet_name] = _embed_gemini(full_text)

    # 6 Embeddings simultan / asynchron abarbeiten
    results_768 = await asyncio.gather(*tasks_768.values())
    results_3072 = await asyncio.gather(*tasks_3072.values())

    vectors = {}
    for i, facet_name in enumerate(tasks_768.keys()):
        v768 = results_768[i]
        v3072 = results_3072[i]

        if v768 is None and v3072 is None:
            logger.error(f"Embedding fuer Facette '{facet_name}' (768 & 3072) fehlgeschlagen.")
            return None

        vectors[facet_name] = {
            "768": v768,
            "3072": v3072
        }

    return vectors


async def embed_6_lenses(document: str) -> Optional[dict[str, dict[str, list[float]]]]:
    """
    Erzeugt 6 Perspektiv-Embeddings fuer ein Dokument (Funnel-Ansatz: 768 & 3072 dim).
    Jede Linse bekommt ihren Prefix + den Dokumenttext.

    Returns:
        {"math": {"768": [...], "3072": [...]}, ...} oder None
    """
    tasks_768 = {}
    tasks_3072 = {}
    for lens_name, prefix in LENS_PREFIXES.items():
        full_text = prefix + document
        # Parallel für 6 Linsen x 2 Dimensionen
        tasks_768[lens_name] = _embed_ollama(full_text)
        tasks_3072[lens_name] = _embed_gemini(full_text)

    # 12 Embeddings simultan (bzw. asynchron)
    results_768 = await asyncio.gather(*tasks_768.values())
    results_3072 = await asyncio.gather(*tasks_3072.values())

    vectors = {}
    for i, lens_name in enumerate(tasks_768.keys()):
        v768 = results_768[i]
        v3072 = results_3072[i]

        if v768 is None and v3072 is None:
            logger.error(f"Embedding fuer Linse '{lens_name}' (768 & 3072) fehlgeschlagen.")
            return None

        vectors[lens_name] = {
            "768": v768,
            "3072": v3072
        }

    return vectors


def _format_vector_for_pg(vec: list[float] | list[complex]) -> str:
    """Formatiert einen Vektor als pgvector-kompatiblen String."""
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"


def _multiview_ssh_config() -> tuple[str, str, str, str]:
    """SSH-Key, Host, User, Docker-Psql-Cmd aus .env (VPS_* / MULTIVIEW_*)."""
    key = (
        os.getenv("MULTIVIEW_SSH_KEY")
        or os.getenv("VPS_SSH_KEY")
        or os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY")
        or ""
    ).strip()
    host = (os.getenv("MULTIVIEW_VPS_HOST") or os.getenv("VPS_HOST") or "187.77.68.250").strip()
    user = (os.getenv("MULTIVIEW_VPS_USER") or os.getenv("VPS_USER") or "root").strip()
    docker_psql = (
        os.getenv("MULTIVIEW_PG_DOCKER_CMD")
        or "docker exec -i atlas_postgres_state psql -U atlas_admin -d atlas_state"
    ).strip()
    return key, host, user, docker_psql


async def _run_pg_sql(sql: str, timeout: int = 30) -> tuple[bool, str]:
    """Fuehrt SQL auf dem VPS-pgvector aus (SSH + Docker psql)."""
    import subprocess

    ssh_key, vps_host, vps_user, docker_cmd = _multiview_ssh_config()
    if not ssh_key or not os.path.isfile(ssh_key):
        logger.error("Multi-View pgvector: SSH-Key fehlt oder nicht lesbar.")
        return False, "ssh_key_missing"

    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
        "-i", ssh_key, f"{vps_user}@{vps_host}", docker_cmd,
    ]

    try:
        def _run():
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            return subprocess.run(
                ssh_cmd,
                input=sql.encode("utf-8"),
                capture_output=True,
                timeout=timeout,
                env=env,
            )

        result = await asyncio.to_thread(_run)
        err = (result.stderr or b"").decode("utf-8", errors="replace")
        out = (result.stdout or b"").decode("utf-8", errors="replace")
        # check only for hard psql errors, not just the word ERROR in content
        if result.returncode != 0 or "ERROR:" in err.upper() or "ERROR:" in out.upper():
            logger.error(f"pgvector SQL fehlgeschlagen rc={result.returncode}: {err or out}")
            return False, err or out
        return True, out
    except Exception as e:
        logger.error(f"pgvector SQL Exception: {e}")
        return False, str(e)


async def insert_multi_view(
    doc_id: str,
    document: str,
    vectors: dict[str, dict[str, list[float] | list[complex]]],
    score: float | complex,
    pairs: list[dict],
    source_collection: str = "",
    metadata: dict = None,
    e6_anchor_id: int = None,
    v_multimodal: list[float] | list[complex] = None,
    modality: str = "text",
) -> bool:
    """Fuegt ein Multi-View-Embedding ein.
    Duale Topologie: Text/Meta in PostgreSQL, Vektoren in ChromaDB (isolierte Raeume).
    Kardanische Faltung: Komplexe Resonanzen werden in Real/Imag gefaltet.
    """
    from src.logic_core.resonance_membrane import assert_resonance_float, assert_infrastructure_int
    from src.logic_core.crystal_grid_engine import CrystalGridEngine

    # 1. Kardanischer Sprung & Validierung
    # Trigger Operator ? falls Druck zu hoch (snapping)
    snapped_score = CrystalGridEngine.apply_operator_query(abs(score))
    assert_resonance_float("score", snapped_score)
    if e6_anchor_id is not None:
        assert_infrastructure_int("e6_anchor_id", e6_anchor_id)

    # 0. Bias Damper & Atlas Hardening
    document = _apply_bias_damper(document)
    is_hardened = _is_atlas_hardened(snapped_score)

    def _dq(s: str, base: str) -> str:
        t = base
        while f"${t}$" in s:
            t += "x"
        return f"${t}$" + s + f"${t}$"

    meta = metadata or {}
    meta["modality"] = modality
    meta["atlas_hardened"] = is_hardened

    # Kardanische Metadaten
    if isinstance(snapped_score, complex):
        meta["score_real"] = snapped_score.real
        meta["score_imag"] = snapped_score.imag
    else:
        meta["score_real"] = float(snapped_score)
        meta["score_imag"] = 0.0

    meta_s = json.dumps(meta, ensure_ascii=False)
    pairs_s = json.dumps(pairs, ensure_ascii=False)
    row_id = str(uuid.uuid4())
    anchor = e6_anchor_id if e6_anchor_id is not None else 0
    doc_id_esc = doc_id.replace("'", "''")
    src_esc = (source_collection or "").replace("'", "''")

    # --- 1. ASYNC INGEST IN CHROMADB (Isolierte Vektor-Raeume) ---
    is_3_facets = "keywords" in vectors
    is_ai = metadata.get("speaker") == "gemini" or metadata.get("is_ai") is True

    # Kardanische Trennung: Nutze AI-Collections für Gemini-Content
    # AUSSER wenn Atlas-gehärtet -> dann darf es in den User-Raum (oder wir bleiben bei der Trennung mit höherem Trust)
    active_facet_map = AI_FACET_TO_COLLECTION if (is_ai and not is_hardened) else FACET_TO_COLLECTION

    if is_3_facets:
        chroma_tasks = []
        for facet, v_data in vectors.items():
            collection_name = active_facet_map.get(facet)
            if not collection_name: continue

            # --- DUAL VECTOR TOPOLOGY ---
            # 1. Outer Push (P-Vektor): We use 768 dim (Ollama) for ChromaDB triage
            v_fast = v_data.get("768")
            if not v_fast: continue

            async def _add_to_chroma(c_name=collection_name, v=v_fast):
                try:
                    col = await chroma_client.get_collection(c_name)
                    await asyncio.to_thread(
                        col.add,
                        ids=[row_id],
                        embeddings=[v],
                        metadatas=[{"doc_id": doc_id, "source": source_collection, "is_ai": is_ai, "hardened": is_hardened}]
                    )
                except Exception as e:
                    logger.error(f"[Multi-View] Chroma Ingest ({c_name}) fehlgeschlagen: {e}")

            chroma_tasks.append(_add_to_chroma())

        if chroma_tasks:
            await asyncio.gather(*chroma_tasks)

    # --- 2. INGEST IN POSTGRESQL (Kausal-Archiv / int-Domäne) ---
    # 2. Inner Pull (S-Vektor): We fold Gemini 3072 -> 6144 for pgvector structural integrity
    score_val = abs(snapped_score) # Magnitude für Legacy-Spalte
    if is_3_facets:
        # Mapping: keywords -> v_keywords, semantics -> v_semantics, media -> v_media
        # 2. Inner Pull (S-Vektor): We fold Gemini 3072 -> 6144 for pgvector structural integrity
        v_k = _format_vector_for_pg(_fold_complex(vectors["keywords"]["3072"])) if vectors.get("keywords", {}).get("3072") else "NULL"
        v_s = _format_vector_for_pg(_fold_complex(vectors["semantics"]["3072"])) if vectors.get("semantics", {}).get("3072") else "NULL"
        v_m = _format_vector_for_pg(_fold_complex(vectors["media_descriptors"]["3072"])) if vectors.get("media_descriptors", {}).get("3072") else "NULL"

        cols = "id, doc_id, document, source_collection, v_keywords, v_semantics, v_media, convergence_score, convergence_pairs, e6_anchor_id, metadata"
        vals = f"'{row_id}', '{doc_id_esc}', {_dq(document, 'd')}, '{src_esc}', '{v_k}', '{v_s}', '{v_m}', {score_val}, {_dq(pairs_s, 'p')}::jsonb, {anchor}, {_dq(meta_s, 'm')}::jsonb"
    else:
        # Legacy 6-Lenses Pfad
        fast_cols = "v_math_768, v_physics_768, v_philo_768, v_bio_768, v_info_768, v_narr_768"
        deep_cols = "v_math, v_physics, v_philo, v_bio, v_info, v_narr"
        cols = f"id, doc_id, document, source_collection, {fast_cols}, {deep_cols}, convergence_score, convergence_pairs, e6_anchor_id, metadata"
        v768 = {k: _format_vector_for_pg(v["768"]) if v["768"] else "NULL" for k, v in vectors.items()}
        v3072 = {k: _format_vector_for_pg(v["3072"]) if v["3072"] else "NULL" for k, v in vectors.items()}
        vals = (
            f"'{row_id}', '{doc_id_esc}', {_dq(document, 'd')}, '{src_esc}', "
            f"'{v768['math']}', '{v768['physics']}', '{v768['philo']}', '{v768['bio']}', '{v768['info']}', '{v768['narr']}', "
            f"'{v3072['math']}', '{v3072['physics']}', '{v3072['philo']}', '{v3072['bio']}', '{v3072['info']}', '{v3072['narr']}', "
            f"{score_val}, {_dq(pairs_s, 'p')}::jsonb, {anchor}, {_dq(meta_s, 'm')}::jsonb"
        )

    vals = vals.replace("'NULL'", "NULL")
    if v_multimodal:
        cols += ", v_multimodal"
        vals += f", '{_format_vector_for_pg(v_multimodal)}'"

    sql = f"INSERT INTO multi_view_embeddings ({cols}) VALUES ({vals}) ON CONFLICT (id) DO NOTHING;"
    ok, _ = await _run_pg_sql(sql)
    return ok


def _convergence_level(score: float) -> str:
    if score >= CONVERGENCE_TOTAL:
        return "TOTAL"
    if score >= CONVERGENCE_STRONG:
        return "STARK"
    if score >= CONVERGENCE_PARTIAL:
        return "PARTIAL"
    return "DIVERGENT"


async def search_multi_view(
    query: str,
    limit: int = 5,
    source_collection: str = None,
    use_3072: bool = True,
    use_3_facets: bool = True,
    include_ai: bool = False, # Standardmäßig skeptische Exklusion von KI-Halluzinationen
    torus_mode: bool = False, # Torus-Lauf: Simultan über alle Collections
) -> list[dict]:
    """Sucht nach Dokumenten.
    Duale Topologie: Vektor-Suche in ChromaDB (float), Hydrierung via PostgreSQL (int).
    Push-Pull-Suche: Nutzt 768 dim für Triage in Chroma, 6144 dim in PG.
    Torus-Mode: Erweitert die Suche auf alle Domänen für maximale Reibung.
    """
    # 1. Vektorisierung (Immer lokal für Triage)
    vec_768 = await embed_local(query)
    if not vec_768:
        return []

    results_map = {} # row_id -> {similarity, count}

    # --- 2. ASYNC VEKTOR-SUCHE IN CHROMADB (Outer Push) ---
    if use_3_facets:
        # Tesserakt-Suche: Simultan gegen alle Facetten (User + ggf. AI)
        facet_collections = list(FACET_TO_COLLECTION.values())
        if include_ai:
            facet_collections.extend(AI_FACET_TO_COLLECTION.values())

        # Torus-Mode: Wir suchen nicht nur in der Ziel-Collection, sondern ueberall
        # Chroma query filtert normalerweise via Metadata.
        where_filter = {}
        if source_collection and not torus_mode:
            where_filter = {"source": source_collection}

        async def _query_col(col_name):
            try:
                from src.network.chroma_client import get_collection
                col = await get_collection(col_name)
                # Chroma query liefert Distanzen (kleiner = besser)
                res = await asyncio.to_thread(
                    col.query,
                    query_embeddings=[vec_768],
                    n_results=limit * 2,
                    where=where_filter if where_filter else None
                )
                if res["ids"] and res["ids"][0]:
                    for i, row_id in enumerate(res["ids"][0]):
                        dist = res["distances"][0][i]
                        sim = 1.0 - dist # Umwandlung in Aehnlichkeit

                        # Skeptischer Filter: KI-Content wird künstlich gedämpft (Baryonic Delta)
                        if col_name in AI_FACET_TO_COLLECTION.values():
                            sim *= TRUST_AI

                        if row_id not in results_map:
                            results_map[row_id] = {"sim": sim, "hits": 1}
                        else:
                            results_map[row_id]["sim"] += sim
                            results_map[row_id]["hits"] += 1
            except Exception as e:
                logger.error(f"[Multi-View] Search {col_name} failed: {e}")

        await asyncio.gather(*[_query_col(c) for c in facet_collections])

        # Sortieren nach akkumulierter Simularitaet / Hits (Konvergenz)
        sorted_ids = sorted(results_map.keys(), key=lambda x: results_map[x]["sim"], reverse=True)[:limit]
        if not sorted_ids: return []

        # Hydrierung aus PG
        id_list = ", ".join(f"'{sid}'" for sid in sorted_ids)
        sql = f"SELECT id, doc_id, document, source_collection, metadata FROM multi_view_embeddings WHERE id IN ({id_list});"

    else:
        # Legacy Pfad: Suche direkt in PG (pgvector)
        v_str = _format_vector_for_pg(vec)
        col_to_use = "v_philo" if (use_3072 and len(vec) == 3072) else "v_philo_768"
        sql = f"""
        SELECT id, doc_id, document, source_collection, metadata,
               (1 - ({col_to_use} <=> '{v_str}')) as similarity
        FROM multi_view_embeddings
        """
        if source_collection:
            sql += f" WHERE source_collection = '{source_collection.replace(chr(39), chr(39)+chr(39))}'"
        sql += f" ORDER BY similarity DESC LIMIT {limit};"

    # --- 3. DATEN ABHOLEN & PARSEN ---
    ok, out = await _run_pg_sql(sql)
    if not ok: return []

    results = []
    # Parsing (analog zu bestehendem Code, aber flexibler)
    import re
    # Matcht row_id (UUID) am Zeilenanfang
    blocks = re.split(r"^(?=[a-f0-9-]{36}\|)", out, flags=re.MULTILINE)

    for block in blocks:
        if not block.strip(): continue
        parts = block.strip().split("|")
        if len(parts) >= 4:
            try:
                row_id = parts[0].strip()
                doc_id = parts[1].strip()
                # document kann multiline sein
                sim = 0.0
                if not use_3_facets:
                    sim = float(parts[-1].strip())
                    meta = parts[-2].strip()
                    source = parts[-3].strip()
                    document = "|".join(parts[2:-3]).strip()
                else:
                    sim = results_map.get(row_id, {}).get("sim", 0.0)
                    meta = parts[-1].strip()
                    source = parts[-2].strip()
                    document = "|".join(parts[2:-2]).strip()

                results.append({
                    "doc_id": doc_id,
                    "document": document,
                    "source": source,
                    "metadata": meta,
                    "similarity": sim
                })
            except Exception: continue

    # Nochmals sortieren falls aus Chroma (da PG-Abfrage unsortiert sein koennte)
    if use_3_facets:
        results = sorted(results, key=lambda x: x["similarity"], reverse=True)

    return results


# --- BIAS DAMPER (Filter für KI-Rauschen/Halluzinationen) ---
BIAS_DAMPER_PATTERNS = [
    r"(?i)^\[AUDIO/WHISPER\]\s+Vielen Dank\.?$",
    r"(?i)^\[ESKALATION\]\s+Hier ist (die|eine) (detaillierte\s+)?Analyse.*:",
    r"(?i)^Hier ist (die|eine) (detaillierte\s+)?Analyse.*:",
    r"(?i)^Zusammenfassend lässt sich sagen.*$",
    r"(?i)^Ich hoffe, (das|dies) hilft.*$",
    r"(?i)^Solltest du weitere Fragen haben, stehe ich gerne zur Verfügung\.?$"
]

def _apply_bias_damper(text: str) -> str:
    """Bereinigt den Text von KI-Rauschen (Whisper-Artefakte, Gemini-Einleitungen)."""
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        is_noise = False
        for pattern in BIAS_DAMPER_PATTERNS:
            if re.match(pattern, line.strip()):
                is_noise = True
                break
        if not is_noise:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

async def ingest_document(
    document: str,
    doc_id: str = None,
    source_collection: str = "",
    metadata: dict = None,
    use_3_facets: bool = True,
) -> Optional[dict]:
    """
    Vollstaendige Ingest-Pipeline: Text -> 3 Facetten (Standard) -> Konvergenz -> pgvector.
    CORE-Eichung: use_3_facets ist nun Standard für maximale Gedächtnis-Resonanz.
    """
    # 0. Bias Damper (Clean-up before vectorization)
    document = _apply_bias_damper(document)

    if not doc_id:
        doc_id = str(uuid.uuid4())[:12]

    vectors = await (embed_3_facets(document) if use_3_facets else embed_6_lenses(document))
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

    level = _convergence_level(score)
    logger.info(f"[Multi-View] {doc_id}: score={score:.4f} ({level}), inserted={success}")

    return {
        "doc_id": doc_id,
        "convergence_score": score,
        "convergence_level": level,
        "pairs": pairs,
        "success": success,
    }


async def ingest_multimodal(
    document: str,
    file_path: str,
    mime_type: str,
    doc_id: str = None,
    source_collection: str = "",
    metadata: dict = None,
    use_3_facets: bool = False,
) -> Optional[dict]:
    """Multimodale Ingest-Pipeline: Text-Repr. + Mediendatei → 6 Linsen ODER 3 Facetten + Multimodal-Vektor → pgvector.

    Asynchrone Entkopplung: Parameter 'use_3_facets' wechselt dynamisch auf die neuen Spalten,
    waehrend das nativ-multimodale Embedding aus der Mediendatei (Bild/Audio/Video/PDF)
    unveraendert in den 3072-dim Vektorraum ueberfuehrt wird.
    """
    if not doc_id:
        doc_id = str(uuid.uuid4())[:12]

    # 0. Bias Damper (Clean-up before vectorization)
    document = _apply_bias_damper(document)

    modality_map = {
        "image/jpeg": "image", "image/png": "image", "image/webp": "image",
        "audio/wav": "audio", "audio/mp3": "audio", "audio/mpeg": "audio",
        "audio/ogg": "audio", "audio/flac": "audio",
        "video/mp4": "video", "video/webm": "video", "video/quicktime": "video",
        "application/pdf": "pdf",
    }
    modality = modality_map.get(mime_type, "mixed")

    # Asynchrone Entkopplung: Wahl zwischen altem und neuem Embedding-Schema
    if use_3_facets:
        text_task = embed_3_facets(document)
    else:
        text_task = embed_6_lenses(document)

    mm_task = embed_multimodal(file_path, mime_type, text_context=document[:500])

    vectors, v_mm = await asyncio.gather(text_task, mm_task)

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
        v_multimodal=v_mm,
        modality=modality,
    )

    level = _convergence_level(score)
    logger.info(
        "[Multi-View] %s: score=%.4f (%s) modality=%s mm_vec=%s inserted=%s",
        doc_id, score, level, modality, "OK" if v_mm else "FAIL", success,
    )

    return {
        "doc_id": doc_id,
        "convergence_score": score,
        "convergence_level": level,
        "modality": modality,
        "multimodal_embedded": v_mm is not None,
        "pairs": pairs,
        "success": success,
    }
