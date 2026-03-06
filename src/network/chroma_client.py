# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
ChromaDB-Client für MTHO_CORE (lokal oder remote auf VPS).
Liest Konfiguration aus .env; bei CHROMA_HOST → HttpClient (VPS), sonst PersistentClient (lokal).
Collections laut Schnittstelle: argos_knowledge_graph, core_brain_registr, krypto_scan_buffer.
"""
import os
from dotenv import load_dotenv

load_dotenv("c:/MTHO_CORE/.env")

# Remote (VPS): CHROMA_HOST + CHROMA_PORT (Standard 8000)
CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip()
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
# Lokal (Dreadnought/Windows), wenn CHROMA_HOST leer
CHROMA_LOCAL_PATH = os.getenv("CHROMA_LOCAL_PATH", r"c:\MTHO_CORE\data\chroma_db")

# Collection-Namen laut 03_DATENBANK_VECTOR_STORE_OSMIUM.md + ATLAS Neocortex V1
COLLECTION_ARGOS = "argos_knowledge_graph"
COLLECTION_CORE_BRAIN = "core_brain_registr"
COLLECTION_KRYTO_SCAN = "krypto_scan_buffer"
COLLECTION_EVENTS = "events"
COLLECTION_INSIGHTS = "insights"
COLLECTION_SESSION_LOGS = "session_logs"
COLLECTION_CORE_DIRECTIVES = "core_directives"
COLLECTION_SIMULATION_EVIDENCE = "simulation_evidence"
COLLECTION_WUJI = "wuji_field"


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
            metadata={"description": f"MTHO_CORE Collection: {name}"},
        )
    return client.get_collection(name=name)


def is_remote() -> bool:
    """True, wenn ChromaDB auf VPS (CHROMA_HOST) genutzt wird."""
    return bool(CHROMA_HOST)


def is_configured() -> bool:
    """True, wenn ChromaDB nutzbar ist (CHROMA_HOST gesetzt oder lokaler Pfad konfigurierbar)."""
    return bool(CHROMA_HOST) or bool(CHROMA_LOCAL_PATH)


# Dimension für events/insights (Metadata-Only-Queries; Embedding optional)
EVENTS_EMBEDDING_DIM = 384


def get_events_collection():
    """Collection 'events' für ATLAS Neocortex (Sensor-Events). add() mit embeddings=[[0]*EVENTS_EMBEDDING_DIM]."""
    return get_collection(COLLECTION_EVENTS, create_if_missing=True)


def add_event_to_chroma(event_id: str, event: dict, metadata_flat: dict) -> bool:
    """Fügt ein Event in ChromaDB events ein. metadata_flat: nur str/int/float/bool."""
    try:
        col = get_events_collection()
        col.add(
            ids=[event_id],
            embeddings=[[0.0] * EVENTS_EMBEDDING_DIM],
            metadatas=[metadata_flat],
            documents=[__import__("json").dumps(event, ensure_ascii=False)],
        )
        return True
    except Exception:
        return False


def get_session_logs_collection():
    """Collection 'session_logs' fuer externe/interne Gespraechs-Sessions (semantische Suche)."""
    return get_collection(COLLECTION_SESSION_LOGS, create_if_missing=True)


def get_core_directives_collection():
    """Collection 'core_directives' fuer Ring-0/1 Direktiven (Dual-Write mit System-Prompts)."""
    return get_collection(COLLECTION_CORE_DIRECTIVES, create_if_missing=True)


def add_session_turn(
    turn_id: str,
    document: str,
    source: str,
    session_date: str,
    turn_number: int,
    speaker: str,
    topics: str = "",
    ring_level: int = 2,
) -> bool:
    """Fuegt einen einzelnen Turn eines Session-Logs in ChromaDB ein.
    Nutzt ChromaDB Default-Embedding (semantische Suche moeglich).
    """
    try:
        col = get_session_logs_collection()
        col.add(
            ids=[turn_id],
            documents=[document],
            metadatas=[{
                "source": source,
                "session_date": session_date,
                "turn_number": turn_number,
                "speaker": speaker,
                "topics": topics,
                "ring_level": ring_level,
            }],
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Session-Turn Ingest fehlgeschlagen: {e}")
        return False


def query_session_logs(query_text: str, n_results: int = 5, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Session-Logs. Gibt relevante Turns zurueck."""
    try:
        col = get_session_logs_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        return col.query(**kwargs)
    except Exception as e:
        print(f"[ChromaDB] Session-Log Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


def query_core_directives(query_text: str, n_results: int = 3, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Core-Direktiven (Ring-0/1). Gibt relevante Direktiven zurueck."""
    try:
        col = get_core_directives_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        return col.query(**kwargs)
    except Exception as e:
        print(f"[ChromaDB] Core Directives Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


def get_simulation_evidence_collection():
    """Collection 'simulation_evidence' fuer Simulationstheorie-Indizien."""
    return get_collection(COLLECTION_SIMULATION_EVIDENCE, create_if_missing=True)


def add_simulation_evidence(
    evidence_id: str,
    document: str,
    category: str,
    strength: str,
    branch_count: int = 0,
    source: str = "atlas",
    date_added: str = "",
    auto_classify: bool = True,
) -> bool:
    """Fuegt ein Simulationstheorie-Indiz in ChromaDB ein.

    strength: 'fundamental' (Stamm/Knotenpunkt) | 'strong' (grosser Ast) | 'moderate' (Ast)
    branch_count: Wieviele unabhaengige Erkenntnisaeste hier zusammenlaufen (Knotenpunkt-Staerke)
    auto_classify: Quaternaere Klassifikation (L/P/I/S) automatisch durchfuehren (V6+)
    """
    try:
        col = get_simulation_evidence_collection()
        metadata = {
            "category": category,
            "strength": strength,
            "branch_count": branch_count,
            "source": source,
            "date_added": date_added or __import__("datetime").date.today().isoformat(),
        }

        if auto_classify:
            try:
                from src.logic_core.quaternary_codec import enrich_evidence_metadata
                metadata = enrich_evidence_metadata(document, metadata)
            except Exception:
                pass

        col.upsert(
            ids=[evidence_id],
            documents=[document],
            metadatas=[metadata],
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Simulation Evidence Ingest fehlgeschlagen: {e}")
        return False


def query_simulation_evidence(query_text: str, n_results: int = 10, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Simulationstheorie-Indizien."""
    try:
        col = get_simulation_evidence_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        return col.query(**kwargs)
    except Exception as e:
        print(f"[ChromaDB] Simulation Evidence Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


def add_evidence_validated(
    document: str,
    evidence_id: str,
    category: str = None,
    strength: str = "mittel",
    branch_count: int = 5,
    source: str = "manual",
) -> dict:
    """Validierte Evidence-Ingest-Pipeline: Klassifiziert, validiert temporal, fuegt ein, prueft Chargaff.

    Wenn category nicht angegeben: automatisch via quaternary_codec.classify_evidence(document).
    Fuehrt temporale Konsistenzpruefung durch und analysiert Chargaff-Balance nach Insertion.

    Returns:
        {"success": bool, "classification": dict, "temporal": dict, "chargaff": dict}
    """
    result = {"success": False, "classification": {}, "temporal": {}, "chargaff": {}}

    try:
        try:
            from src.logic_core.quaternary_codec import classify_evidence, analyze_chargaff_balance
        except ImportError:
            from logic_core.quaternary_codec import classify_evidence, analyze_chargaff_balance

        cls = classify_evidence(document)
        resolved_category = category if category else cls.base.value
        result["classification"] = {
            "base": cls.base.value,
            "confidence": cls.confidence,
            "scores": cls.scores,
            "complement": cls.complement.value,
            "auto_classified": category is None,
        }

        try:
            try:
                from src.logic_core.temporal_validator import validate_temporal_consistency
            except ImportError:
                from logic_core.temporal_validator import validate_temporal_consistency
            result["temporal"] = validate_temporal_consistency(document)
        except Exception as e:
            result["temporal"] = {"error": str(e)}

        strength_map = {
            "schwach": "moderate",
            "mittel": "moderate",
            "stark": "strong",
            "fundamental": "fundamental",
            "moderate": "moderate",
            "strong": "strong",
        }
        mapped_strength = strength_map.get(strength.lower(), strength)

        success = add_simulation_evidence(
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
                col = get_simulation_evidence_collection()
                all_data = col.get(include=["metadatas"])
                distribution = {"L": 0, "P": 0, "I": 0, "S": 0}
                for m in all_data["metadatas"]:
                    qb = m.get("qbase", "")
                    if qb in distribution:
                        distribution[qb] += 1
                chargaff = analyze_chargaff_balance("", distribution)
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


def get_wuji_field_collection():
    """Collection 'wuji_field' fuer einheitliches Gedaechtnis (GQA F8)."""
    return get_collection(COLLECTION_WUJI, create_if_missing=True)


def query_wuji_field(
    query_text: str,
    n_results: int = 10,
    type_filter: str | list[str] | None = None,
    where_filter: dict | None = None,
) -> dict:
    """Semantische Suche im Wuji-Feld mit optionalem type-Filter.

    type_filter: Einzelner type (str) oder Liste (z.B. ["evidence", "directive"]).
    where_filter: Zusaetzliche ChromaDB where-Bedingungen (werden mit type_filter kombiniert).
    """
    try:
        col = get_wuji_field_collection()
        where = where_filter.copy() if where_filter else {}
        if type_filter is not None:
            if isinstance(type_filter, str):
                where["type"] = type_filter
            else:
                where["type"] = {"$in": list(type_filter)}
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where:
            kwargs["where"] = where
        return col.query(**kwargs)
    except Exception as e:
        print(f"[ChromaDB] Wuji-Field Query fehlgeschlagen: {e}")
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}


def query_wuji_via_gravitator(
    query_text: str,
    n_results: int = 10,
    top_k_types: int = 3,
) -> dict:
    """Routet via Gravitator zu relevanten Types, fragt wuji_field ab, merged Ergebnisse."""
    try:
        from src.logic_core.gravitator import route_to_wuji

        targets = route_to_wuji(query_text, top_k=top_k_types)
        if not targets:
            return query_wuji_field(query_text, n_results=n_results)

        types = [t.type for t in targets]
        result = query_wuji_field(
            query_text,
            n_results=n_results,
            type_filter=types,
        )
        return result
    except Exception as e:
        print(f"[ChromaDB] Wuji-via-Gravitator fehlgeschlagen: {e}")
        return query_wuji_field(query_text, n_results=n_results)


def add_core_directive(directive_id: str, document: str, category: str, ring_level: int = 0) -> bool:
    """Schreibt eine Ring-0/1 Direktive in ChromaDB (Dual-Write Partner zu System-Prompts)."""
    try:
        col = get_core_directives_collection()
        col.upsert(
            ids=[directive_id],
            documents=[document],
            metadatas=[{
                "category": category,
                "ring_level": ring_level,
            }],
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Core Directive Ingest fehlgeschlagen: {e}")
        return False


def add_wuji_observation(
    observation: str,
    source: str = "vision_daemon",
    metadata: dict = None,
) -> bool:
    """Fuegt eine Beobachtung in das Wuji-Feld ein (Quantum Observer).
    
    Das Wuji-Feld ist der Speicher fuer rohe, ungefilterte Wahrnehmungen,
    die noch nicht zu "Wissen" (Argos) kondensiert sind.
    """
    try:
        col = get_wuji_field_collection()
        import datetime
        import uuid

        meta = metadata or {}
        meta.update({
            "source": source,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "observation",
        })

        col.add(
            ids=[str(uuid.uuid4())],
            documents=[observation],
            metadatas=[meta],
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Wuji Observation failed: {e}")
        return False
