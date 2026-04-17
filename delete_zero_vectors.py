import chromadb
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))
from src.config.vps_public_ports import CHROMA_UVMY_HOST_PORT

load_dotenv(_ROOT / ".env")

vps = os.getenv("VPS_HOST", "").strip()
port = int(os.getenv("CHROMA_PORT", str(CHROMA_UVMY_HOST_PORT)))

print(f"Connecting to ChromaDB at {vps}:{port}...")
c = chromadb.HttpClient(host=vps, port=port)

col = c.get_collection('events')
count = col.count()
print(f"Collection 'events' has {count} items.")

# Fetch all embeddings to find zero-vectors
# 2841 is small enough to fetch in one go
batch_size = 500
offset = 0
zero_ids = []

while offset < count:
    print(f"Fetching offset {offset}...")
    res = col.get(include=['embeddings'], limit=batch_size, offset=offset)
    ids = res.get('ids', [])
    embeddings = res.get('embeddings', [])

    if not ids:
        break

    for i, emb in enumerate(embeddings):
        if emb is not None and all(float(v) == 0.0 for v in emb):
            zero_ids.append(ids[i])

    offset += batch_size

print(f"Found {len(zero_ids)} zero-vectors.")

if zero_ids:
    print(f"Deleting {len(zero_ids)} zero-vectors in batches...")
    for i in range(0, len(zero_ids), batch_size):
        batch_ids = zero_ids[i:i+batch_size]
        col.delete(ids=batch_ids)
        print(f"Deleted batch of {len(batch_ids)} items.")

    print(f"Deletion complete. New count: {col.count()}")
else:
    print("No zero-vectors found.")
