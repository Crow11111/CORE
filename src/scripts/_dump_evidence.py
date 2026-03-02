import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from network.chroma_client import get_simulation_evidence_collection
import json

col = get_simulation_evidence_collection()
data = col.get(include=["documents", "metadatas"])

items = []
for i, eid in enumerate(data["ids"]):
    m = data["metadatas"][i]
    items.append({
        "id": eid,
        "branches": m.get("branch_count", 0),
        "strength": m.get("strength", "?"),
        "category": m.get("category", "?"),
        "doc": data["documents"][i][:120],
    })

items.sort(key=lambda x: -x["branches"])
for it in items:
    print(json.dumps(it, ensure_ascii=False))
