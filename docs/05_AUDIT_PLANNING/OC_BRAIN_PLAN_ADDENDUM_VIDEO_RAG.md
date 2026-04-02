<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- Addendum: YouTube Gemini-2-RAG + Orchestrierungs-Direktive
<!-- ============================================================
-->

# OC Brain Reaktivierung – Plan-Addendum: Video-RAG & Orchestrierung

**Bezug:** Ursprünglicher Operationsplan (OC Brain Reaktivierung, lokales LLM, ChromaDB, WhatsApp).
**Status:** Verbindliche Erweiterung. Ausführung durch **Team-Lead / Experten**, nicht durch Orchestrator selbst.

---

## 1. YouTube-Video verbindlich einbinden

**Quelle:** [Dieses Google Modell verändert RAG](https://www.youtube.com/watch?v=LNhvEO_JWVM&t=346s) (LNhvEO_JWVM).

**Bereits im Repo:**
- Transkript: [`docs/05_AUDIT_PLANNING/YOUTUBE_TRANSCRIPT_GEMINI_RAG.md`](YOUTUBE_TRANSCRIPT_GEMINI_RAG.md)
- Kurzreferenz: [`docs/05_AUDIT_PLANNING/STATUS_OS_MIGRATION_PAUSE.md`](STATUS_OS_MIGRATION_PAUSE.md) (Abschnitt „Video-Review“)

**Kern des Videos (für RAG-Architektur):**
- **Gemini 2 Embeddings** (multimodal): Text, Bilder, Video, Audio, PDF in einer Vektordatenbank; semantische Suche über alle Modalitäten.
- **Chunking:** Text bis 6000 Token + 500 Overlap; PDF je 5–6 Seiten; Video 120 s; Audio 75 s.
- **Embedding-Dimension:** 3072 (Google-Empfehlung).
- **Vektordatenbank:** Im Video Supabase; für CORE verbindlich **ChromaDB** (laut [CORE_CHROMADB_SCHEMA.md](../02_ARCHITECTURE/CORE_CHROMADB_SCHEMA.md)).
- **Similarity Threshold:** typisch ~0,3; TopK konfigurierbar.

**Auftrag an das Team (nicht durch Orchestrator ausführen):**
1. **DB-Expert / System-Architect:** Transkript `YOUTUBE_TRANSCRIPT_GEMINI_RAG.md` in ChromaDB einpflegen – Collection `world_knowledge` (oder laut Schema passende Collection), mehrstufiges Chunking (Abschnitt → Absatz → Satz), Metadaten `source=YOUTUBE_TRANSCRIPT_GEMINI_RAG`, `category=rag_reference`.
2. **System-Architect:** RAG-Pipeline (Strang D des Plans) an diese Architektur anlehnen: Chunking-Limits, Embedding-Dimension (falls Wechsel auf Gemini-Embeddings geplant), Similarity-Threshold in Konfiguration.
3. **Team-Lead:** Token-Budgets und Reihenfolge gemäß Plan halten; ChromaDB und `.cursorrules` für Effizienz und einheitliche Constraints nutzen.

---

## 2. Orchestrierungs-Direktive

- **Orchestrator (CEO/Schicht 0):** Analysiert, plant, instanziert Task Forces, weist Budgets zu. Führt keine operativen Schritte selbst aus (kein eigenes Ingest, kein eigener Code für RAG-Anbindung).
- **Ausführung:** Nur durch **Team-Lead** und zugewiesene Experten (db-expert, system-architect, security-expert, networking-expert) gemäß [task_parallelization_internal.mdc](../../.cursor/rules/task_parallelization_internal.mdc) und [.cursorrules](../../.cursorrules) (CORE-OD-03: Delegation).
- **ChromaDB:** Alle Vektor- und Ingest-Entscheidungen an [CORE_CHROMADB_SCHEMA.md](../02_ARCHITECTURE/CORE_CHROMADB_SCHEMA.md) und bestehende Collections (inkl. `mth_user_profile`, `world_knowledge`) anbinden.
- **Ziel:** Tokendurchsatz verringern, Output verbessern, Effizienz über klare Rollen und Nutzung der bestehenden Regeln/Schema steigern.

---

## 3. Verweise

| Thema | Pfad |
|-------|------|
| ChromaDB Schema | `docs/02_ARCHITECTURE/CORE_CHROMADB_SCHEMA.md` |
| Transkript Video | `docs/05_AUDIT_PLANNING/YOUTUBE_TRANSCRIPT_GEMINI_RAG.md` |
| Video-Review/Kern | `docs/05_AUDIT_PLANNING/STATUS_OS_MIGRATION_PAUSE.md` |
| Delegation | `.cursorrules` (CORE-OD-03), `.cursor/rules/task_parallelization_internal.mdc` |
| MTH-Profil / Quellen | `docs/01_CORE_DNA/MTH_PROFILE_ARCHIVE.md`, `src/scripts/ingest_mth_profile_to_chroma.py` |

---

*Addendum erstellt 2026-03-14. YouTube-Video und RAG-Referenz sind verbindlicher Teil der OC Brain / RAG-Operation; Umsetzung liegt bei den beauftragten Experten.*


[LEGACY_UNAUDITED]
