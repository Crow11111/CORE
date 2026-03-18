# OC Brain RAG-Pipeline (Strang D)

**Bezug:** [OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md](../05_AUDIT_PLANNING/OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md), [OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md](../05_AUDIT_PLANNING/OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md)

**Ablauf:** Query → ChromaDB (world_knowledge + mth_user_profile) → Context → LLM (Ollama/Gemini/Claude via OpenClaw).

---

## Pipeline

| Schritt | Komponente | Beschreibung |
|--------|------------|--------------|
| 1 | Query | Nutzeranfrage oder Agent-Prompt |
| 2 | ChromaDB | Parallele Abfrage: `query_world_knowledge(q, n)`, `query_mth_user_profile(q, n)` |
| 3 | Context | Kombinierte Dokumente als Markdown (Abschnitte world_knowledge, mth_user_profile) |
| 4 | LLM | Kontext als System-/User-Kontext an OpenClaw-Provider (Ollama/Gemini/Claude) |

---

## Implementierung

- **Chroma-Client:** `src/network/chroma_client.py`  
  - `query_world_knowledge()`, `query_mth_user_profile()`, `get_mth_user_profile_collection()`
- **API:** `GET /api/core/knowledge/rag?q=...&n=5`  
  - Route: `src/api/routes/core_knowledge.py` → `get_rag_context()`  
  - Antwort: `{ "ok", "query", "context", "sources": { "world_knowledge", "mth_user_profile" } }`
- **OpenClaw-Anbindung:** OC/Tool kann diese Route aufrufen und `context` in den LLM-Prompt injizieren. Kein eigener RAG-Tool-Code in OpenClaw nötig, sofern ein HTTP-Call zu CORE möglich ist.

---

## Video-RAG-Architektur (Addendum)

Chunking und Thresholds laut [OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md](../05_AUDIT_PLANNING/OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md):

- Text: bis 6000 Token + 500 Overlap; Similarity-Threshold ~0,3; TopK konfigurierbar.
- Collections: `world_knowledge` (z. B. YOUTUBE_TRANSCRIPT_GEMINI_RAG), `mth_user_profile` (Tier 1–3).

Schema: [CORE_CHROMADB_SCHEMA.md](CORE_CHROMADB_SCHEMA.md).

---

## Todo (falls noch nicht umgesetzt)

- [ ] OpenClaw-Tool/Skill, das vor LLM-Aufruf `GET /api/core/knowledge/rag?q=<aktuelle Nutzerfrage>&n=5` aufruft und Kontext in den Prompt einfügt.
- [ ] Optional: Similarity-Threshold (z. B. 0.3) in Konfiguration und bei Query anwenden (Filter nach Distance).
