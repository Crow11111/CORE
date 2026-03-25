
import os
import asyncio
import chromadb
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

async def ensure_kardanic_collections():
    host = os.getenv('CHROMA_HOST', '187.77.68.250')
    port = int(os.getenv('CHROMA_PORT', 8000))
    client = chromadb.HttpClient(host=host, port=port)

    collections = [
        "mv_keywords", "mv_semantics", "mv_media",
        "ai_mv_keywords", "ai_mv_semantics", "ai_mv_media"
    ]

    # We expect 768 dimensions for P-Vektor (Agency) in Chroma
    expected_dim = 768

    for col_name in collections:
        try:
            col = client.get_or_create_collection(col_name)
            count = col.count()

            # Check existing dimension if not empty
            if count > 0:
                data = col.get(limit=1, include=['embeddings'])
                actual_dim = len(data['embeddings'][0])
                if actual_dim != expected_dim:
                    logger.warning(f"Collection {col_name} has wrong dimension: {actual_dim} != {expected_dim}. Recreating...")
                    client.delete_collection(col_name)
                    client.create_collection(col_name)
                    logger.info(f"Recreated collection {col_name}")
                else:
                    logger.info(f"Collection {col_name} is already kardanic (dim={actual_dim})")
            else:
                # Empty, just ensure it's there
                logger.info(f"Collection {col_name} is empty, ready for kardanic ingests.")
        except Exception as e:
            logger.error(f"Error checking collection {col_name}: {e}")

if __name__ == "__main__":
    asyncio.run(ensure_kardanic_collections())
