# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import sys
import logging
from aiohttp import web
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════
# MTHO SYNC RELAY (THE CRADLE)
# ═══════════════════════════════════════════════════════════
# Empfängt Live-Regel-Injections von G-MTHO (Cloud).
# Empfängt Vektor-Syncs von G-MTHO → lokale ChromaDB.
# Schreibt direkt in .cursor/rules/MTHO_LIVE_INJECT.mdc
# ═══════════════════════════════════════════════════════════

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

load_dotenv(os.path.join(ROOT, ".env"))
logging.basicConfig(level=logging.INFO, format='[OMEGA SYNC] %(message)s')

SECRET = os.getenv("MTHO_WEBHOOK_SECRET")
TARGET_FILE = ".cursor/rules/MTHO_LIVE_INJECT.mdc"

if not SECRET:
    logging.warning("MTHO_WEBHOOK_SECRET not found in .env! Relay is insecure/broken.")

async def handle_inject(request):
    """
    Endpoint: POST /inject
    Header: X-Mtho-Secret: <MTHO_WEBHOOK_SECRET>
    Body: {"content": "..."}
    """
    # 1. Security Check
    auth_header = request.headers.get('X-Mtho-Secret')
    if not SECRET or auth_header != SECRET:
        logging.warning(f"Unauthorized injection attempt from {request.remote}")
        return web.Response(status=401, text="Unauthorized: Invalid Secret")

    # 2. Payload Parsing
    try:
        data = await request.json()
        content = data.get('content')
        if content is None:
             return web.Response(status=400, text="Missing 'content' field")
    except Exception as e:
        return web.Response(status=400, text=f"Invalid JSON: {str(e)}")

    # 3. Execution (Overwrite Rule)
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(TARGET_FILE), exist_ok=True)
        
        # Write content
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        bytes_written = len(content.encode('utf-8'))
        logging.info(f"Injected bytes: {bytes_written}")
        
        return web.json_response({
            "status": "success", 
            "bytes_written": bytes_written,
            "target": TARGET_FILE
        })
        
    except Exception as e:
        logging.error(f"Write failed: {e}")
        return web.Response(status=500, text=f"Internal Write Error: {str(e)}")

async def handle_vectors(request):
    """
    Endpoint: POST /vectors
    Header: X-Mtho-Secret: <MTHO_WEBHOOK_SECRET>
    Body: {
        "collection": "wuji_field" | "simulation_evidence" | ...,
        "ids": ["id1", "id2", ...],
        "documents": ["doc1", "doc2", ...],
        "embeddings": [[0.1, 0.2, ...], ...],  # optional
        "metadatas": [{...}, {...}, ...]       # optional
    }
    """
    auth_header = request.headers.get('X-Mtho-Secret')
    if not SECRET or auth_header != SECRET:
        logging.warning(f"Unauthorized vector sync attempt from {request.remote}")
        return web.Response(status=401, text="Unauthorized: Invalid Secret")

    try:
        data = await request.json()
        collection_name = data.get('collection', 'wuji_field')
        ids = data.get('ids')
        documents = data.get('documents')
        embeddings = data.get('embeddings')
        metadatas = data.get('metadatas')

        if not ids:
            return web.Response(status=400, text="Missing 'ids' field")
        if not documents:
            return web.Response(status=400, text="Missing 'documents' field")

    except Exception as e:
        return web.Response(status=400, text=f"Invalid JSON: {str(e)}")

    try:
        from src.network.chroma_client import get_collection

        col = get_collection(collection_name, create_if_missing=True)

        # Sanitize metadatas
        if metadatas:
            clean_metas = []
            for m in metadatas:
                if m is None:
                    clean_metas.append({})
                else:
                    clean_metas.append({
                        k: (v if isinstance(v, (str, int, float, bool)) else str(v))
                        for k, v in m.items()
                    })
            metadatas = clean_metas

        upsert_kwargs = {
            "ids": ids,
            "documents": documents,
        }
        if embeddings:
            upsert_kwargs["embeddings"] = embeddings
        if metadatas:
            upsert_kwargs["metadatas"] = metadatas

        col.upsert(**upsert_kwargs)

        count_after = col.count()
        logging.info(f"Vectors synced: {len(ids)} → {collection_name} (total: {count_after})")

        return web.json_response({
            "status": "success",
            "collection": collection_name,
            "synced": len(ids),
            "total": count_after
        })

    except Exception as e:
        logging.error(f"Vector sync failed: {e}")
        return web.Response(status=500, text=f"ChromaDB Error: {str(e)}")


async def handle_status(request):
    """
    Endpoint: GET /status
    Returns ChromaDB collections and counts.
    """
    try:
        from src.network.chroma_client import get_chroma_client, is_remote

        client = get_chroma_client()
        collections = client.list_collections()

        result = {
            "mode": "remote" if is_remote() else "local",
            "collections": {}
        }
        for col in collections:
            result["collections"][col.name] = col.count()

        return web.json_response(result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


# App Definition
app = web.Application()
app.add_routes([
    web.post('/inject', handle_inject),
    web.post('/vectors', handle_vectors),
    web.get('/status', handle_status),
])

if __name__ == '__main__':
    logging.info(f"Starting MTHO CRADLE RELAY on port 8049...")
    logging.info(f"Endpoints: /inject (rules), /vectors (chroma sync), /status")
    logging.info(f"Target file: {TARGET_FILE}")
    web.run_app(app, port=8049)
