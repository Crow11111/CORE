# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Gravitator – Selbstorganisierendes Collection-Routing.

Duale Topologie:
  ChromaDB  = Routing-Cache, schnelle Discovery (384/768 dim)
  pgvector  = Deep Persistenz, Multi-View 6-Linsen + multimodal (3072 dim)

Routing-Embeddings laufen LOKAL (Ollama nomic-embed-text, 768 dim, 0 Kosten).
Gemini Embedding 2 (3072 dim) nur fuer Persistenz in pgvector.

Kennfeld = ChromaDB + pgvector Topologie. Kein starres Overlay.
Schwingung = Input schwingt bis zur hoechsten Resonanz (Delta -> 0.049).
Refresh-Takt: Zentroide werden periodisch neu berechnet.
"""
from __future__ import annotations

import asyncio
import logging
import math
import os
import time
from dataclasses import dataclass, field

from src.logic_core.takt_gate import check_takt_zero
from src.logic_core.crystal_grid_engine import CrystalGridEngine
from src.config.core_state import BARYONIC_DELTA

logger = logging.getLogger("core.gravitator")

CENTROID_SAMPLE_SIZE = 50
REFRESH_INTERVAL_SEC = 300
MIN_COLLECTION_SIZE = 2


@dataclass
class CollectionTarget:
    name: str
    score: float
    type: str


@dataclass
class _CollectionNode:
    """Dynamisch entdeckter Knoten im Gravitationsfeld."""
    name: str
    count: int
    centroid: list[float]
    sample_docs: list[str] = field(default_factory=list)
    discovered_at: float = 0.0
    dim: int = 0
    source: str = "chroma"


_SKIP_COLLECTIONS = {"test_hang_diag", "user_state_vectors", "relationships",
                      "atlas_identity", "entities", "insights"}

# ── Dynamischer Cache ──
_field_nodes: list[_CollectionNode] = []
_field_built_at: float = 0.0
_field_lock = asyncio.Lock()


def _get_chroma_ef():
    """ChromaDB Default-EF (all-MiniLM-L6-v2, 384 dim) — fuer ChromaDB-Zentroid-Routing."""
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    return DefaultEmbeddingFunction()


def _embed_local_sync(text: str) -> list[float]:
    """Lokales Embedding via Ollama nomic-embed-text (768 dim, 0 Kosten)."""
    import httpx
    host = os.getenv("OLLAMA_LOCAL_HOST", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(f"{host}/api/embed", json={"model": model, "input": text})
        resp.raise_for_status()
        return resp.json()["embeddings"][0]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or len(a) == 0:
        return BARYONIC_DELTA
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return BARYONIC_DELTA
    return dot / (na * nb)


def _mean_vector(vectors: list[list[float]]) -> list[float]:
    """Zentroid: Mittelwert aller Vektoren."""
    if not vectors:
        return []
    dim = len(vectors[0])
    centroid = [0.0] * dim
    for v in vectors:
        for i in range(dim):
            centroid[i] += v[i]
    n = len(vectors)
    return [c / n for c in centroid]


def _discover_and_build_sync() -> list[_CollectionNode]:
    """Entdeckt alle ChromaDB-Collections, samplet Embeddings, berechnet Zentroide."""
    import chromadb
    from dotenv import load_dotenv
    load_dotenv("/OMEGA_CORE/.env")

    nodes: list[_CollectionNode] = []

    vps_host = os.getenv("VPS_HOST", "").strip()
    vps_port = int(os.getenv("CHROMA_PORT", "32768"))

    sources: list[tuple[str, chromadb.ClientAPI]] = []

    if vps_host:
        try:
            remote = chromadb.HttpClient(host=vps_host, port=vps_port)
            remote.heartbeat()
            sources = sources + [("vps", remote)]
        except Exception as e:
            logger.warning("[GRAVITATOR] VPS ChromaDB nicht erreichbar: %s", e)

    local_path = os.getenv("CHROMA_LOCAL_PATH", "/OMEGA_CORE/chroma_db")
    if os.path.isdir(local_path):
        try:
            local = chromadb.PersistentClient(path=local_path)
            sources = sources + [("local", local)]
        except Exception as e:
            logger.warning("[GRAVITATOR] Lokale ChromaDB Fehler: %s", e)

    now = time.time()

    for source_tag, client in sources:
        try:
            collections = client.list_collections()
        except Exception:
            continue

        for col in collections:
            if col.name in _SKIP_COLLECTIONS:
                continue
            try:
                cnt = col.count()
                if cnt < MIN_COLLECTION_SIZE:
                    continue

                peek = col.peek(limit=min(CENTROID_SAMPLE_SIZE, cnt))
                embeddings = peek.get("embeddings")
                if embeddings is None or len(embeddings) == 0:
                    continue

                real_embs = []
                for emb in embeddings:
                    if emb is not None and not all(float(v) == 0.0 for v in emb):
                        real_embs = real_embs + [[float(v) for v in emb]]

                if len(real_embs) < MIN_COLLECTION_SIZE:
                    continue

                centroid = _mean_vector(real_embs)

                sample_docs = []
                docs = peek.get("documents")
                if docs:
                    for d in docs[:5]:
                        if d:
                            sample_docs = sample_docs + [str(d)[:200]]

                existing = next((n for n in nodes if n.name == col.name), None)
                if existing:
                    if cnt > existing.count:
                        existing.count = cnt
                        existing.centroid = centroid
                        existing.sample_docs = sample_docs
                else:
                    nodes = nodes + [_CollectionNode(
                        name=col.name,
                        count=cnt,
                        centroid=centroid,
                        sample_docs=sample_docs,
                        discovered_at=now,
                    )]

            except Exception as e:
                logger.debug("[GRAVITATOR] Collection %s skip: %s", col.name, e)

    # ── pgvector: Multimodale Collections aus multi_view_embeddings ──
    pg_nodes = _discover_pgvector_collections()
    for pn in pg_nodes:
        existing = next((n for n in nodes if n.name == pn.name), None)
        if existing:
            if pn.count > existing.count:
                existing.count = pn.count
                existing.centroid = pn.centroid
                existing.dim = pn.dim
                existing.source = "pgvector"
        else:
            nodes = nodes + [pn]

    logger.info(
        "[GRAVITATOR] Feld gebaut: %d Knoten, %s",
        len(nodes),
        ", ".join(f"{n.name}({n.count},{n.source})" for n in sorted(nodes, key=lambda x: -x.count)),
    )
    return nodes


def _discover_pgvector_collections() -> list[_CollectionNode]:
    """Entdeckt pgvector-Collections und baut lokale Zentroide (768 dim via Ollama).

    Samplet Dokument-Texte aus jeder Collection, embeddet sie lokal mit
    nomic-embed-text, und berechnet Zentroide im lokalen 768-dim Raum.
    So kann der Gravitator ohne API-Kosten gegen pgvector routen.
    """
    import subprocess
    from dotenv import load_dotenv
    load_dotenv("/OMEGA_CORE/.env")

    ssh_key = (
        os.getenv("MULTIVIEW_SSH_KEY") or os.getenv("VPS_SSH_KEY")
        or os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or ""
    ).strip()
    host = (os.getenv("MULTIVIEW_VPS_HOST") or os.getenv("VPS_HOST") or "").strip()
    user = (os.getenv("MULTIVIEW_VPS_USER") or os.getenv("VPS_USER") or "root").strip()
    docker_cmd = (
        os.getenv("MULTIVIEW_PG_DOCKER_CMD")
        or "docker exec -i atlas_postgres_state psql -U atlas_admin -d atlas_state"
    ).strip()

    if not ssh_key or not os.path.isfile(ssh_key):
        return []

    sql = (
        "SELECT source_collection, COUNT(*) as cnt, "
        "ARRAY_AGG(LEFT(document, 300) ORDER BY convergence_score DESC) as sample_docs "
        "FROM multi_view_embeddings "
        "WHERE source_collection != '' "
        "GROUP BY source_collection "
        "HAVING COUNT(*) >= 2 "
        "ORDER BY cnt DESC;"
    )

    try:
        ssh_cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
            "-i", ssh_key, f"{user}@{host}", docker_cmd,
        ]

        sql_simple = (
            "SELECT source_collection, COUNT(*) as cnt "
            "FROM multi_view_embeddings "
            "WHERE source_collection != '' "
            "GROUP BY source_collection "
            "HAVING COUNT(*) >= 2 "
            "ORDER BY cnt DESC;"
        )
        r = subprocess.run(ssh_cmd, input=sql_simple.encode(), capture_output=True, timeout=20)
        if r.returncode != 0:
            return []

        lines = r.stdout.decode("utf-8", errors="replace").strip().split("\n")
        collections: list[tuple[str, int]] = []
        for line in lines:
            parts = line.strip().split("|")
            if len(parts) == 2:
                name = parts[0].strip()
                try:
                    cnt = int(parts[1].strip())
                    if name and not name.startswith("-") and name != "source_collection":
                        collections = collections + [(name, cnt)]
                except ValueError:
                    continue

        if not collections:
            return []

        nodes: list[_CollectionNode] = []
        now = time.time()

        for coll_name, cnt in collections:
            sample_sql = (
                f"SELECT LEFT(document, 300) FROM multi_view_embeddings "
                f"WHERE source_collection = '{coll_name}' "
                f"ORDER BY convergence_score DESC LIMIT 5;"
            )
            r2 = subprocess.run(ssh_cmd, input=sample_sql.encode(), capture_output=True, timeout=15)
            sample_docs = []
            if r2.returncode == 0:
                for sline in r2.stdout.decode("utf-8", errors="replace").strip().split("\n"):
                    txt = sline.strip()
                    if txt and not txt.startswith("-") and not txt.startswith("(") and txt != "left":
                        sample_docs = sample_docs + [txt[:300]]

            centroid = []
            if sample_docs:
                try:
                    combined = " ".join(sample_docs[:3])[:500]
                    centroid = _embed_local_sync(combined)
                except Exception as e:
                    logger.debug("[GRAVITATOR] pgvector Centroid-Embed Fehler fuer %s: %s", coll_name, e)

            nodes = nodes + [_CollectionNode(
                name=f"pg:{coll_name}",
                count=cnt,
                centroid=centroid,
                sample_docs=sample_docs[:3],
                discovered_at=now,
                dim=768 if centroid else 0,
                source="pgvector",
            )]

        logger.debug("[GRAVITATOR] pgvector: %d Collections mit lokalen Zentroiden", len(nodes))
        return nodes

    except Exception as e:
        logger.debug("[GRAVITATOR] pgvector Discovery Fehler: %s", e)
        return []


async def _ensure_field() -> list[_CollectionNode]:
    """Stellt sicher, dass das Gravitationsfeld aktuell ist."""
    global _field_nodes, _field_built_at

    now = time.time()
    if _field_nodes and (now - _field_built_at) < REFRESH_INTERVAL_SEC:
        return _field_nodes

    async with _field_lock:
        if _field_nodes and (now - _field_built_at) < REFRESH_INTERVAL_SEC:
            return _field_nodes

        nodes = await asyncio.to_thread(_discover_and_build_sync)
        if nodes:
            _field_nodes = nodes
            _field_built_at = time.time()
        return _field_nodes


async def refresh_field():
    """Erzwingt Neuaufbau des Gravitationsfeldes."""
    global _field_built_at
    _field_built_at = 0.0
    return await _ensure_field()


async def route(
    query_text: str,
    top_k: int = 3,
    threshold: float = 0.22,
    multimodal_file: str = None,
    multimodal_mime: str = None,
) -> list[CollectionTarget]:
    """Routet query_text (und optional eine Mediendatei) zu den relevantesten Collections.

    Dual-Path Routing:
      ChromaDB-Nodes: via DefaultEmbeddingFunction (384 dim)
      pgvector-Nodes: via Gemini Embedding 2 (3072 dim, multimodal)
    """
    gate_open = await check_takt_zero()
    if not gate_open:
        logger.info("[GRAVITATOR] Takt 0 Veto: '%s...'", query_text[:50])
        return []

    if not query_text or not query_text.strip():
        return []

    nodes = await _ensure_field()
    if not nodes:
        logger.warning("[GRAVITATOR] Leeres Feld — keine Collections entdeckt")
        return []

    chroma_nodes = [n for n in nodes if n.source == "chroma" and n.centroid]
    pg_nodes = [n for n in nodes if n.source == "pgvector"]

    scored: list[tuple[str, float]] = []

    # ChromaDB-Routing: ChromaDB Default-EF (384 dim) → Zentroid-Vergleich
    if chroma_nodes:
        try:
            def _embed_chroma():
                ef = _get_chroma_ef()
                return ef([query_text.strip()])[0]
            query_emb_chroma = await asyncio.to_thread(_embed_chroma)

            for node in chroma_nodes:
                if len(query_emb_chroma) != len(node.centroid):
                    continue
                score = CrystalGridEngine.calculate_resonance(
                    list(query_emb_chroma), list(node.centroid),
                )
                scored = scored + [(node.name, score)]
        except Exception as e:
            logger.warning("[GRAVITATOR] ChromaDB Routing Fehler: %s", e)

    # pgvector-Routing: Lokales Ollama Embedding (768 dim) → Zentroid-Vergleich
    pg_with_centroid = [n for n in pg_nodes if n.centroid]
    if pg_with_centroid:
        try:
            query_emb_local = await asyncio.to_thread(_embed_local_sync, query_text.strip())
            for node in pg_with_centroid:
                if len(query_emb_local) != len(node.centroid):
                    continue
                score = CrystalGridEngine.calculate_resonance(
                    list(query_emb_local), list(node.centroid),
                )
                scored = scored + [(node.name, score)]
        except Exception as e:
            logger.warning("[GRAVITATOR] pgvector Routing Fehler: %s", e)
            for node in pg_with_centroid:
                scored = scored + [(node.name, threshold)]

    scored.sort(key=lambda x: -x[1])
    matches = [(name, s) for name, s in scored if s >= threshold][:top_k]

    if not matches:
        if scored:
            best_name, best_score = scored[0]
            return [CollectionTarget(name=best_name, score=best_score, type="fallback")]
        return []

    return [
        CollectionTarget(name=name, score=score, type="dynamic")
        for name, score in matches
    ]


async def route_to_context(
    query_text: str,
    top_k: int = 3,
    threshold: float = 0.22,
) -> list[CollectionTarget]:
    targets = await route(query_text, top_k=top_k, threshold=threshold)
    return [
        CollectionTarget(name="context_field", score=t.score, type=t.type)
        for t in targets
    ]


def get_field_status() -> dict:
    """Liefert aktuellen Feld-Zustand fuer /status oder Telemetrie."""
    return {
        "nodes": len(_field_nodes),
        "chroma_nodes": sum(1 for n in _field_nodes if n.source == "chroma"),
        "pgvector_nodes": sum(1 for n in _field_nodes if n.source == "pgvector"),
        "collections": [
            {
                "name": n.name, "count": n.count, "source": n.source,
                "dim": n.dim or (len(n.centroid) if n.centroid else 0),
                "age_sec": round(time.time() - n.discovered_at),
            }
            for n in sorted(_field_nodes, key=lambda x: -x.count)
        ],
        "built_at": _field_built_at,
        "refresh_interval": REFRESH_INTERVAL_SEC,
    }
