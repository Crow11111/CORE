import os
import sys
from pathlib import Path

import chromadb

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))
from src.config.vps_public_ports import CHROMA_UVMY_HOST_PORT

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
CHROMA_HOST = os.getenv("VPS_HOST", "187.77.68.250").strip()
CHROMA_PORT = int(os.getenv("CHROMA_PORT", str(CHROMA_UVMY_HOST_PORT)))
COLLECTION_NAME = "ha_events"

try:
    # 1. Connect to ChromaDB
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    print(f"Successfully connected to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}")

    # 2. Get the collection
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"Accessed collection '{COLLECTION_NAME}'.")

    # 3. Get all items to count them before deletion
    items_before = collection.get()
    count_before = len(items_before['ids'])
    print(f"Found {count_before} documents in '{COLLECTION_NAME}' before deletion.")

    # 4. Delete all documents from the collection if there are any
    if count_before > 0:
        collection.delete(ids=items_before['ids'])
        print(f"Successfully deleted {count_before} documents from '{COLLECTION_NAME}'.")
    else:
        print("Collection is already empty. No documents to delete.")


    # 5. Verification
    items_after = collection.get()
    count_after = len(items_after['ids'])
    print(f"Verification: Found {count_after} documents in '{COLLECTION_NAME}' after deletion.")

    if count_after == 0:
        print("✅ Verification successful: Collection is empty.")
    else:
        print("❌ Verification failed: Collection is NOT empty.")

    print("\n--- ChromaDB Purge Report ---")
    print(f"Items deleted: {count_before}")
    print(f"Items remaining: {count_after}")
    print("----------------------------")


except Exception as e:
    print(f"An error occurred: {e}")

