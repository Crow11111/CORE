# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
ChromaDB-Client für MTHO_CORE (lokal oder remote auf VPS).
Liest Konfiguration aus .env; bei CHROMA_HOST → HttpClient (VPS), sonst PersistentClient (lokal).
Collections laut Schnittstelle: knowledge_graph, core_brain_registr, krypto_scan_buffer.

[UPDATE 2026-03-06] ASYNC I/O ENFORCED (Simultanität).
Alle I/O-Methoden sind nun async und nutzen asyncio.to_thread.
"""
import os
import asyncio
import json
import datetime
import uuid
from dotenv import load_dotenv

load_dotenv("c:/MTHO_CORE/.env")

# Remote (VPS): CHROMA_HOST + CHROMA_PORT (Standard 8000)
CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip()
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
# Lokal (Dreadnought/Windows), wenn CHROMA_HOST leer
CHROMA_LOCAL_PATH = os.getenv("CHROMA_LOCAL_PATH", r"c:\MTHO_CORE\data\chroma_db")

# Collection-Namen laut 03_DATENBANK_VECTOR_STORE_OSMIUM.md + MTHO Neocortex V1
COLLECTION_KNOWLEDGE_GRAPH = "knowledge_graph"
COLLECTION_CORE_BRAIN = "core_brain_registr"
COLLECTION_KRYTO_SCAN = "krypto_scan_buffer"
COLLECTION_EVENTS = "events"
COLLECTION_INSIGHTS = "insights"
COLLECTION_SESSION_LOGS = "session_logs"
COLLECTION_CORE_DIRECTIVES = "core_directives"
COLLECTION_SIMULATION_EVIDENCE = "simulation_evidence"
COLLECTION_CONTEXT = "context_field"


import threading

_chroma_singleton = None
_chroma_lock = threading.Lock()


def _get_chroma_client_sync():
    """Thread-safe Singleton: liefert immer dieselbe ChromaDB-Instanz."""
    global _chroma_singleton
    if _chroma_singleton is not None:
        return _chroma_singleton

    with _chroma_lock:
        if _chroma_singleton is not None:
            return _chroma_singleton

        try:
            import chromadb
        except ImportError:
            raise ImportError("chromadb nicht installiert: pip install chromadb")

        if CHROMA_HOST:
            _chroma_singleton = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        else:
            if not os.path.exists(CHROMA_LOCAL_PATH):
                os.makedirs(CHROMA_LOCAL_PATH)
            _chroma_singleton = chromadb.PersistentClient(path=CHROMA_LOCAL_PATH)

    return _chroma_singleton

async def get_chroma_client():
    """Liefert ChromaDB-Client (Async Wrapper)."""
    return await asyncio.to_thread(_get_chroma_client_sync)


def _get_collection_sync(name: str, create_if_missing: bool = True):
    client = _get_chroma_client_sync()
    if create_if_missing:
        return client.get_or_create_collection(
            name=name,
            metadata={"description": f"MTHO_CORE Collection: {name}"},
        )
    return client.get_collection(name=name)

async def get_collection(name: str = COLLECTION_KNOWLEDGE_GRAPH, create_if_missing: bool = True):
    """Holt die angegebene Collection (Async)."""
    return await asyncio.to_thread(_get_collection_sync, name, create_if_missing)


def is_remote() -> bool:
    """True, wenn ChromaDB auf VPS (CHROMA_HOST) genutzt wird."""
    return bool(CHROMA_HOST)


def is_configured() -> bool:
    """True, wenn ChromaDB nutzbar ist (CHROMA_HOST gesetzt oder lokaler Pfad konfigurierbar)."""
    return bool(CHROMA_HOST) or bool(CHROMA_LOCAL_PATH)


# Dimension für events/insights (Metadata-Only-Queries; Embedding optional)
EVENTS_EMBEDDING_DIM = 384


async def get_events_collection():
    """Collection 'events' für MTHO Neocortex (Sensor-Events). add() mit embeddings=[[0]*EVENTS_EMBEDDING_DIM]."""
    return await get_collection(COLLECTION_EVENTS, create_if_missing=True)


async def add_event_to_chroma(event_id: str, event: dict, metadata_flat: dict) -> bool:
    """Fügt ein Event in ChromaDB events ein. Async."""
    try:
        col = await get_events_collection()
        await asyncio.to_thread(
            col.add,
            ids=[event_id],
            embeddings=[[0.0] * EVENTS_EMBEDDING_DIM],
            metadatas=[metadata_flat],
            documents=[json.dumps(event, ensure_ascii=False)]
        )
        return True
    except Exception:
        return False


async def get_session_logs_collection():
    """Collection 'session_logs' fuer externe/interne Gespraechs-Sessions (semantische Suche)."""
    return await get_collection(COLLECTION_SESSION_LOGS, create_if_missing=True)


async def get_core_directives_collection():
    """Collection 'core_directives' fuer Ring-0/1 Direktiven (Dual-Write mit System-Prompts)."""
    return await get_collection(COLLECTION_CORE_DIRECTIVES, create_if_missing=True)


async def add_session_turn(
    turn_id: str,
    document: str,
    source: str,
    session_date: str,
    turn_number: int,
    speaker: str,
    topics: str = "",
    ring_level: int = 2,
) -> bool:
    """Fuegt einen einzelnen Turn eines Session-Logs in ChromaDB ein. Async."""
    try:
        col = await get_session_logs_collection()
        await asyncio.to_thread(
            col.add,
            ids=[turn_id],
            documents=[document],
            metadatas=[{
                "source": source,
                "session_date": session_date,
                "turn_number": turn_number,
                "speaker": speaker,
                "topics": topics,
                "ring_level": ring_level,
            }]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Session-Turn Ingest fehlgeschlagen: {e}")
        return False


async def query_session_logs(query_text: str, n_results: int = 5, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Session-Logs. Async."""
    try:
        col = await get_session_logs_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        return await asyncio.to_thread(col.query, **kwargs)
    except Exception as e:
        print(f"[ChromaDB] Session-Log Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


async def query_core_directives(query_text: str, n_results: int = 3, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Core-Direktiven (Ring-0/1). Async."""
    try:
        col = await get_core_directives_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        return await asyncio.to_thread(col.query, **kwargs)
    except Exception as e:
        print(f"[ChromaDB] Core Directives Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


async def get_simulation_evidence_collection():
    """Collection 'simulation_evidence' fuer Simulationstheorie-Indizien."""
    return await get_collection(COLLECTION_SIMULATION_EVIDENCE, create_if_missing=True)


async def add_simulation_evidence(
    evidence_id: str,
    document: str,
    category: str,
    strength: str,
    branch_count: int = 0,
    source: str = "mtho",
    date_added: str = "",
    auto_classify: bool = True,
) -> bool:
    """Fuegt ein Simulationstheorie-Indiz in ChromaDB ein. Async."""
    try:
        col = await get_simulation_evidence_collection()
        metadata = {
            "category": category,
            "strength": strength,
            "branch_count": branch_count,
            "source": source,
            "date_added": date_added or datetime.date.today().isoformat(),
        }

        if auto_classify:
            # Note: quaternary_codec is synchronous logic/math, okay to run in thread but 
            # ideally should be pure logic. Importing might be IO bound.
            try:
                def _enrich():
                    from src.logic_core.quaternary_codec import enrich_evidence_metadata
                    return enrich_evidence_metadata(document, metadata)
                metadata = await asyncio.to_thread(_enrich)
            except Exception:
                pass

        await asyncio.to_thread(
            col.upsert,
            ids=[evidence_id],
            documents=[document],
            metadatas=[metadata]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Simulation Evidence Ingest fehlgeschlagen: {e}")
        return False


async def query_simulation_evidence(query_text: str, n_results: int = 10, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Simulationstheorie-Indizien. Async."""
    try:
        col = await get_simulation_evidence_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        return await asyncio.to_thread(col.query, **kwargs)
    except Exception as e:
        print(f"[ChromaDB] Simulation Evidence Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


async def add_evidence_validated(
    document: str,
    evidence_id: str,
    category: str = None,
    strength: str = "mittel",
    branch_count: int = 5,
    source: str = "manual",
) -> dict:
    """Validierte Evidence-Ingest-Pipeline. Async."""
    result = {"success": False, "classification": {}, "temporal": {}, "chargaff": {}}

    try:
        # Complex logic, heavy imports -> wrap in thread
        def _process_logic():
            try:
                from src.logic_core.quaternary_codec import classify_evidence, analyze_chargaff_balance
            except ImportError:
                # Fallback for paths
                from logic_core.quaternary_codec import classify_evidence, analyze_chargaff_balance

            cls = classify_evidence(document)
            resolved_category = category if category else cls.base.value
            
            try:
                try:
                    from src.logic_core.temporal_validator import validate_temporal_consistency
                except ImportError:
                    from logic_core.temporal_validator import validate_temporal_consistency
                temporal = validate_temporal_consistency(document)
            except Exception as e:
                temporal = {"error": str(e)}
                
            return cls, resolved_category, temporal

        cls, resolved_category, temporal = await asyncio.to_thread(_process_logic)
        
        result["classification"] = {
            "base": cls.base.value,
            "confidence": cls.confidence,
            "scores": cls.scores,
            "complement": cls.complement.value,
            "auto_classified": category is None,
        }
        result["temporal"] = temporal

        strength_map = {
            "schwach": "moderate",
            "mittel": "moderate",
            "stark": "strong",
            "fundamental": "fundamental",
            "moderate": "moderate",
            "strong": "strong",
        }
        mapped_strength = strength_map.get(strength.lower(), strength)

        success = await add_simulation_evidence(
            evidence_id=evidence_id,
            document=document,
            category=resolved_category,
            strength=mapped_strength,
            branch_count=branch_count,
            source=source,
            auto_classify=True,
        )
        result["success"] = success

        if success:
            try:
                col = await get_simulation_evidence_collection()
                
                def _analyze_chargaff():
                    try:
                        from src.logic_core.quaternary_codec import analyze_chargaff_balance
                        all_data = col.get(include=["metadatas"])
                        distribution = {"L": 0, "P": 0, "I": 0, "S": 0}
                        for m in all_data["metadatas"]:
                            qb = m.get("qbase", "")
                            if qb in distribution:
                                distribution[qb] += 1
                        return analyze_chargaff_balance("", distribution)
                    except Exception:
                        return None

                chargaff = await asyncio.to_thread(_analyze_chargaff)
                if chargaff:
                    result["chargaff"] = {
                        "distribution": chargaff.distribution,
                        "ratios": chargaff.ratios,
                        "deviation": chargaff.chargaff_deviation,
                        "missing_types": chargaff.missing_types,
                    }
            except Exception as e:
                result["chargaff"] = {"error": str(e)}

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    return result


async def get_context_field_collection():
    """Collection 'context_field' fuer einheitliches Gedaechtnis (GQA F8). Async."""
    return await get_collection(COLLECTION_CONTEXT, create_if_missing=True)


async def query_context_field(
    query_text: str,
    n_results: int = 10,
    type_filter: str | list[str] | None = None,
    where_filter: dict | None = None,
) -> dict:
    """Semantische Suche im context field. Async."""
    try:
        col = await get_context_field_collection()
        where = where_filter.copy() if where_filter else {}
        if type_filter is not None:
            if isinstance(type_filter, str):
                where["type"] = type_filter
            else:
                where["type"] = {"$in": list(type_filter)}
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where:
            kwargs["where"] = where
        return await asyncio.to_thread(col.query, **kwargs)
    except Exception as e:
        print(f"[ChromaDB] Context-Field Query fehlgeschlagen: {e}")
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}


async def query_context_via_gravitator(
    query_text: str,
    n_results: int = 10,
    top_k_types: int = 3,
) -> dict:
    """Routet via Gravitator zu relevanten Types, fragt context_field ab. Async."""
    try:
        from src.logic_core.gravitator import route_to_context

        targets = await route_to_context(query_text, top_k=top_k_types)
        if not targets:
            return await query_context_field(query_text, n_results=n_results)

        types = [t.type for t in targets]
        result = await query_context_field(
            query_text,
            n_results=n_results,
            type_filter=types,
        )
        return result
    except Exception as e:
        print(f"[ChromaDB] Context-via-Gravitator fehlgeschlagen: {e}")
        return await query_context_field(query_text, n_results=n_results)


async def add_core_directive(directive_id: str, document: str, category: str, ring_level: int = 0) -> bool:
    """Schreibt eine Ring-0/1 Direktive in ChromaDB. Async."""
    try:
        col = await get_core_directives_collection()
        await asyncio.to_thread(
            col.upsert,
            ids=[directive_id],
            documents=[document],
            metadatas=[{
                "category": category,
                "ring_level": ring_level,
            }]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Core Directive Ingest fehlgeschlagen: {e}")
        return False


async def add_context_observation(
    observation: str,
    source: str = "vision_daemon",
    metadata: dict = None,
) -> bool:
    """Fuegt eine Beobachtung in das context field ein. Async."""
    try:
        col = await get_context_field_collection()
        
        meta = metadata or {}
        meta.update({
            "source": source,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "observation",
        })

        await asyncio.to_thread(
            col.add,
            ids=[str(uuid.uuid4())],
            documents=[observation],
            metadatas=[meta]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Context Observation failed: {e}")
        return False
