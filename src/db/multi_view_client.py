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

# Gemini text-embedding / aktuelle API: typisch 3072 (Legacy 768 — Tabelle muss passen)
EMBEDDING_DIM_768 = 768
EMBEDDING_DIM_3072 = 3072
EMBEDDING_DIM = EMBEDDING_DIM_3072  # Standard fuer Deep (Stufe 2)


def _gemini_embed_model() -> str:
    """RAG-Vektorisierung: Modell aus Registry (GEMINI_EMBED_MODEL)."""
    from src.ai.model_registry import get_model_for_role
    return (get_model_for_role("embedding") or "gemini-embedding-001").strip()

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


OLLAMA_EMBED_HOST = os.getenv("OLLAMA_LOCAL_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")


async def _embed_ollama(text: str) -> Optional[list[float]]:
    """Lokales Embedding via Ollama nomic-embed-text (768 dim). Kosten: 0."""
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
    """Stufe 1: Lokales Embedding (768 dim, 0 Kosten, ~50ms).

    Fuer Routing, Similarity-Checks, Triage, Gravitator.
    Fallback auf Gemini wenn Ollama nicht erreichbar.
    """
    vec = await _embed_ollama(text)
    if vec:
        return vec
    return await _embed_gemini(text)


async def embed_text(text: str) -> Optional[list[float]]:
    """Stufe 2: Deep Embedding (3072 dim, API-Kosten).

    Fuer Multi-View Persistenz in pgvector (6 Linsen).
    Fallback auf Ollama wenn API nicht erreichbar.
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


def _format_vector_for_pg(vec: list[float]) -> str:
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


async def _run_pg_sql(sql: str) -> tuple[bool, str]:
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
                timeout=30,
                env=env,
            )

        result = await asyncio.to_thread(_run)
        err = (result.stderr or b"").decode("utf-8", errors="replace")
        out = (result.stdout or b"").decode("utf-8", errors="replace")
        if result.returncode != 0 or "ERROR" in err.upper() or "ERROR" in out.upper():
            logger.error(f"pgvector SQL fehlgeschlagen rc={result.returncode}: {err or out}")
            return False, err or out
        return True, out
    except Exception as e:
        logger.error(f"pgvector SQL Exception: {e}")
        return False, str(e)


async def insert_multi_view(
    doc_id: str,
    document: str,
    vectors: dict[str, dict[str, list[float]]],
    score: float,
    pairs: list[dict],
    source_collection: str = "",
    metadata: dict = None,
    e6_anchor_id: int = None,
    v_multimodal: list[float] = None,
    modality: str = "text",
) -> bool:
    """Fuegt ein Multi-View-Embedding in pgvector ein (VPS via SSH + Docker psql).
    Speichert dual-depth Vektoren (768 & 3072) fuer jede Linse.

    v_multimodal: Optionaler nativ-multimodaler Vektor (Bild/Audio/Video/PDF via Gemini Embedding 2).
    modality: text | image | audio | video | pdf | mixed
    """
    from src.logic_core.resonance_membrane import assert_resonance_float, assert_infrastructure_int

    assert_resonance_float("score", score)
    if e6_anchor_id is not None:
        assert_infrastructure_int("e6_anchor_id", e6_anchor_id)
    def _dq(s: str, base: str) -> str:
        t = base
        while f"${t}$" in s:
            t += "x"
        return f"${t}$" + s + f"${t}$"

    meta = metadata or {}
    meta["modality"] = modality
    meta_s = json.dumps(meta, ensure_ascii=False)
    pairs_s = json.dumps(pairs, ensure_ascii=False)
    row_id = str(uuid.uuid4())
    anchor = e6_anchor_id if e6_anchor_id is not None else 0
    doc_id_esc = doc_id.replace("'", "''")
    src_esc = (source_collection or "").replace("'", "''")

    # Spalten fuer 768 (Fast) und 3072 (Deep)
    # v_math, ... sind bereits 3072 (laut psql \d)
    fast_cols = "v_math_768, v_physics_768, v_philo_768, v_bio_768, v_info_768, v_narr_768"
    deep_cols = "v_math, v_physics, v_philo, v_bio, v_info, v_narr"

    cols = (
        f"id, doc_id, document, source_collection, "
        f"{fast_cols}, {deep_cols}, "
        f"convergence_score, convergence_pairs, e6_anchor_id, metadata"
    )

    # Vektoren vorbereiten (768)
    v768 = {k: _format_vector_for_pg(v["768"]) if v["768"] else "NULL" for k, v in vectors.items()}
    # Vektoren vorbereiten (3072)
    v3072 = {k: _format_vector_for_pg(v["3072"]) if v["3072"] else "NULL" for k, v in vectors.items()}

    vals = (
        f"'{row_id}', '{doc_id_esc}', {_dq(document, 'd')}, '{src_esc}', "
        f"'{v768['math']}', '{v768['physics']}', '{v768['philo']}', '{v768['bio']}', '{v768['info']}', '{v768['narr']}', "
        f"'{v3072['math']}', '{v3072['physics']}', '{v3072['philo']}', '{v3072['bio']}', '{v3072['info']}', '{v3072['narr']}', "
        f"{score}, {_dq(pairs_s, 'p')}::jsonb, {anchor}, {_dq(meta_s, 'm')}::jsonb"
    )

    # NULL-Handling (Vermeidung von 'NULL' in Strings)
    for k in v768:
        if v768[k] == "NULL": vals = vals.replace(f"'{v768[k]}'", "NULL")
    for k in v3072:
        if v3072[k] == "NULL": vals = vals.replace(f"'{v3072[k]}'", "NULL")

    # Finales SQL
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
) -> list[dict]:
    """Sucht in pgvector nach dem query-String (RAG via Cosine-Similarity).
    Standardmaessig ueber 3072-dim Vektoren (Deep Resonance).
    """
    # Wenn use_3072, nutzen wir Gemini Embedding (API)
    # Wenn False, nutzen wir Ollama (lokal)
    vec = await (embed_text(query) if use_3072 else embed_local(query))
    if not vec:
        return []

    # v_philo ist 3072 (Deep), v_philo_768 ist 768 (Fast)
    col_to_use = "v_philo" if (use_3072 and len(vec) == 3072) else "v_philo_768"

    # NUTZE -t (tuples only) und -A (unaligned) für saubere Ausgabe
    key, host, user, docker_cmd = _multiview_ssh_config()
    clean_docker_cmd = docker_cmd + " -t -A -F '|'"

    sql = f"""
    SELECT doc_id, document, source_collection, metadata,
           (1 - ({col_to_use} <=> '{v_str}')) as similarity
    FROM multi_view_embeddings
    """
    if source_collection:
        sql += f" WHERE source_collection = '{source_collection.replace(chr(39), chr(39)+chr(39))}'"

    sql += f" ORDER BY similarity DESC LIMIT {limit};"

    import subprocess
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15",
        "-i", key, f"{user}@{host}", clean_docker_cmd,
    ]

    try:
        def _run():
            return subprocess.run(
                ssh_cmd, input=sql.encode("utf-8"), capture_output=True, timeout=30
            )
        result = await asyncio.to_thread(_run)
        out = result.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        logger.error(f"pgvector search error: {e}")
        return []

    results = []
    # DEBUG: Zeige rohe psql-Ausgabe
    # print(f"DEBUG: Raw PSQL output: {repr(out)}")

    # Dirty-Parse: psql -t -A gibt Newlines im Text als echte Newlines aus.
    # Wir suchen nach Zeilen, die mit einem doc_id-Muster (z.B. core_vps_nodes_...) beginnen
    # oder wir parsen den gesamten String nach dem Muster: doc_id | document | source | metadata | similarity

    import re
    # Muster für eine Zeile: doc_id (word chars + -) | text (greedy) | source | meta | similarity (float)
    # Da document alles enthalten kann, ist es schwer. Aber doc_id ist meist strukturiert.
    # Wir probieren es zeilenweise und mergen Chunks.

    # DEBUG: Zeige rohe psql-Ausgabe
    # print(f"DEBUG: Raw PSQL output: {repr(out)}")

    # Dirty-Parse: psql -t -A gibt Newlines im Text als echte Newlines aus.
    # Wir nutzen ein robusteres Muster. Da wir doc_id, document, source, metadata, similarity haben:
    # doc_id ist am Anfang einer Zeile, gefolgt von |, dann Text, dann |source|metadata|similarity
    # similarity ist ein float am Ende einer Zeile

    import re
    # Matcht: doc_id | rest... | source | metadata | float
    # Wir nehmen den gesamten Output und suchen nach dem Muster
    # Wir nehmen den gesamten Output und suchen nach dem Muster
    # doc_id | document (multiline) | source | metadata | similarity
    import re
    # Wir suchen nach doc_id am Anfang einer Zeile, gefolgt von |
    # Dann nehmen wir alles bis zum vor-vor-vorletzten | in dieser "Einheit"
    # Da psql -t -A -F '|' alles flach ausgibt, sind Newlines im document das Problem.

    # Versuche den gesamten Block zu splitten, wo doc_id| am Zeilenanfang steht
    # Wir wissen dass doc_id ein bestimmtes Format hat (word chars, -, _)
    blocks = re.split(r"^(?=[a-zA-Z0-9_\-]+\|)", out, flags=re.MULTILINE)

    for block in blocks:
        if not block.strip(): continue
        # Ein Block sollte doc_id | text... | source | meta | sim sein
        # Aber text kann | enthalten. sim ist am Ende nach dem letzten |
        parts = block.strip().split("|")
        if len(parts) >= 5:
            try:
                sim = float(parts[-1].strip())
                meta = parts[-2].strip()
                source = parts[-3].strip()
                doc_id = parts[0].strip()
                document = "|".join(parts[1:-3]).strip()

                results.append({
                    "doc_id": doc_id,
                    "document": document,
                    "source": source,
                    "metadata": meta,
                    "similarity": sim
                })
            except Exception: continue
    return results


async def ingest_document(
    document: str,
    doc_id: str = None,
    source_collection: str = "",
    metadata: dict = None,
) -> Optional[dict]:
    """
    Vollstaendige Ingest-Pipeline: Text -> 6 Embeddings -> Konvergenz -> pgvector.
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
) -> Optional[dict]:
    """Multimodale Ingest-Pipeline: Text-Repr. + Mediendatei → 6 Linsen + Multimodal-Vektor → pgvector.

    Erzeugt 6 Text-Linsen-Embeddings aus dem document-String UND
    ein nativ-multimodales Embedding aus der Mediendatei (Bild/Audio/Video/PDF)
    via Gemini Embedding 2. Beide landen im selben 3072-dim Vektorraum.
    """
    if not doc_id:
        doc_id = str(uuid.uuid4())[:12]

    modality_map = {
        "image/jpeg": "image", "image/png": "image", "image/webp": "image",
        "audio/wav": "audio", "audio/mp3": "audio", "audio/mpeg": "audio",
        "audio/ogg": "audio", "audio/flac": "audio",
        "video/mp4": "video", "video/webm": "video", "video/quicktime": "video",
        "application/pdf": "pdf",
    }
    modality = modality_map.get(mime_type, "mixed")

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
