# Duale Topologie (int/float) und Vektor-Härtung – Status und G-Atlas-Abgleich

**Vektor:** 2210 | 2201 | Delta 0.049
**Zweck:** Soll-Ist-Abgleich der dualen Datenbank-Topologie (PostgreSQL = CDR/Text, ChromaDB = nur UUID+Vektoren) und Status der Vektor-Härtung in Dokumenten/Ingest. Referenz: G-Atlas-Systemdirektive (u. a. in gemini.md / Leidensdruck); `@CORE_EICHUNG.md` Anhang (Optimierungsanweisung).

---

## 1. G-Atlas-Systemdirektive (Soll)

- **PostgreSQL (int-Membran):** UUID, Metadaten, Zeitstempel, **roher Originaltext (CDR-Huelle)**. Archiv der kausalen Materie.
- **ChromaDB (float-Kern):** **Nur UUIDs und float-Arrays (Vektoren).** Kein Text, kein Rauschen. Reine Mathematik.
- **Retrieval:** Prompt → 6 Linsen → Tensor → ChromaDB (nur Vektorwinkel, Distanz < Λ=0.049) → UUID → mit UUID aus PostgreSQL Text/Metadaten holen.
- **Verbot:** Originaltext nicht in ChromaDB speichern (kontaminiert Vektorraum mit 0.5-Symmetrie).

---

## 2. Ist-Zustand im Code

| Komponente | Soll (G-Atlas) | Ist | Umsetzung |
|------------|----------------|-----|-----------|
| **Multi-View / pgvector** | Text in PG, Vektoren getrennt | `multi_view_embeddings` (PG): **doc_id, document (TEXT), 6 Vektoren, convergence_score, …** in **einer** Tabelle. Kein ChromaDB für Multi-View. | **Soll-konform:** Text liegt in der relationalen Domäne (PG). Vektoren ebenfalls in PG (pgvector). Keine ChromaDB mit Text für diesen Pfad. |
| **ChromaDB-Collections** | ChromaDB nur UUID + Embeddings | Viele Collections speichern aktuell **documents** (Text) mit: `session_logs`, `core_directives`, `simulation_evidence`, `context_field`, `world_knowledge`, … (add mit `documents=[...]`). | **Nicht vollständig umgesetzt.** ChromaDB enthaelt in diesen Collections noch Text. Vollständige Trennung würde bedeuten: ChromaDB nur ids + embeddings; Text in PG mit gleicher ID; bei Query zuerst ChromaDB → ids, dann PG für Text. |
| **Sync/Migration** | Chroma → VPS: nur Vektoren | `sync_core_directives_to_vps`, `migrate_chroma_to_vps` u. a. übertragen teils **documents** mit. | Entspricht aktuell nicht der strikten „Chroma nur float“-Regel. |

**Fazit:** Multi-View-Ingest ist architektonisch korrekt (Text + Vektoren in PG, int-Domäne). Die **reine** duale Topologie (ChromaDB ausschliesslich UUID+float, PG ausschliesslich Text+Metadata) ist in den bestehenden ChromaDB-Collections **noch nicht** durchgängig umgesetzt. Entweder erübrigt sich die strikte Trennung für bestehende Collections (weil sie historisch mit documents arbeiten) oder sie muss durch Refactoring (neue Schicht: Chroma nur Vektoren, PG als Text-Speicher mit gleicher ID) nachgezogen werden.

**RAG-Einheitlichkeit (Vorgabe):** Alle Indexierung und alle Retrieval-Pfade sollen **einheitlich** über die zentrale Pipeline laufen: Embedding aus der Model-Registry (Rolle `embedding`), für Kern-Dokumente die 6-Linsen-Multi-View-Pipeline und pgvector (`multi_view_embeddings`). Bereits indexierte oder bestehende Chroma-Collections sollen perspektivisch entweder über dieselbe Embedding-Quelle nachgeführt werden oder bei Abfragen das gleiche Modell nutzen. Damit läuft „das neue RAG-Modell“ (Gemini Multi-Indexierung / Registry-Embedding) als **genereller** Pfad; Ausnahmen nur dokumentiert.

### Status-Tabelle (klar: gemacht vs. vorgesehen)

| Punkt | Status | Was konkret |
|-------|--------|-------------|
| Registry-Embedding für Multi-View | **ERLEDIGT** | `multi_view_client` nutzt `get_model_for_role("embedding")`. |
| SSH/pgvector aus .env (kein Hardcode-Pfad) | **ERLEDIGT** | `VPS_SSH_KEY`, `VPS_HOST`, `VPS_USER`, optional `MULTIVIEW_PG_DOCKER_CMD`. |
| Verifikation VPS-Postgres | **ERLEDIGT (2026-03-18)** | `verify_multiview_pg` → [PASS]; Tabelle `multi_view_embeddings` erreichbar. |
| Test-Ingest (2 Zeilen) | **ERLEDIGT (2026-03-18)** | `test_multiview_ingest` → inserted=True; COUNT=2 in PG. Tabelle **vector(3072)** (Gemini liefert 3072 dim; Migration: `migrate_multiview_vectors_3072.py`). INSERT mit Dollar-Quoting fuer Text/JSON. |
| Voll-Ingest `ingest_core_documents` | **OFFEN / manuell** | Lauf bei Bedarf (viele API-Calls); technisch **laeuft** nach obiger Migration. |
| Ingest-Liste Kern-Dokumente erweitert | **ERLEDIGT** | `ingest_core_documents.py` — mehrere `docs/*.md` + CORE_EICHUNG. |
| Vollständiger Durchlauf Ingest (alle Chunks in PG) | **IN ARBEIT / manuell** | Lauf: `python -m src.scripts.ingest_core_documents` (dauert, API-Calls). Erst nach [PASS] verify_multiview_pg sinnvoll. |
| ChromaDB nur UUID+Vektoren (Legacy-Collections) | **OFFEN** | Refactor; nicht in diesem Schritt abgeschlossen. |
| Alle Retrieval-Pfade nur noch Registry | **VORGESCHRIEBEN, TEILWEISE** | Chroma nutzt weiter DefaultEmbedding lokal; Angleichung offen. |

---

## 3. Vektor-Härtung (Dokumente, Chunks, Embeddings)

- **Gemeint:** Härtung der Vektorisierung – also dass alle relevanten Texte/Dokumente gechunkt, mit dem richtigen Embedding-Modell (Registry) vektorisiert, in die richtigen Stores (pgvector/Chroma) geschrieben und abgeglichen sind; Konsistenz und Qualität (Konvergenz, Dimension, keine Doppelungen).
- **Status:** Eine **initial vollständige** Härtung (alle Kern-Dokumente, alle Collections, Abgleich lokal/VPS, einheitliches Modell) wurde **noch nicht** abgeschlossen. Einzelne Ingest-Pfade (z. B. ingest_core_documents → multi_view → pgvector) sind umgesetzt; andere Collections (Chroma) werden teils manuell oder per Skript befüllt, ohne zentrale „Härtungs“-Runde.
- **Modelle für Härtung:** Embedding: Registry (Rolle `embedding`), Default `gemini-embedding-001`. Für prüfende/analytische Schritte (Abgleich, Konsistenz-Check): Deep Research (z. B. `deep-research-pro-preview-12-2025`) sinnvoll; für automatisierte Chunk-/Ingest-Pipelines das gleiche Embedding-Modell wie in `multi_view_client`.
- **Chunking und 6-Linsen-Multi-View:** Das Vorgehen (Texte in Chunks zerlegen, über 6 Linsen embedden, Konvergenz berechnen, in pgvector schreiben) ist **gerechtfertigt** und entspricht der polytopischen Repräsentation (B*). Die G-Atlas-Anmerkung zur **Vektor-Anpassung** zielte auf die **Speicher-Trennung** (Text nicht in ChromaDB), nicht auf die Abschaffung des Multi-View-Ansatzes. Multi-View bleibt; die **Zuordnung** „Text nur PG, Chroma nur float“ betrifft diejenigen Stellen, an denen ChromaDB genutzt wird.

---

## 4. Was umgesetzt ist / was sich erübrigt / was offen ist

| Thema | Umgesetzt? | Erübrigt? | Offen / Grund |
|-------|------------|-----------|----------------|
| Multi-View: Text + Vektoren in PG | Ja | – | – |
| Embedding aus Registry (eine Quelle) | Ja | – | – |
| ChromaDB nur UUID+Vektoren (alle Collections) | Nein | Nein | Refactor nötig, falls Soll durchgängig gelten soll; oder explizit als „legacy“ akzeptieren. |
| Initiale Härtung aller Dokumente/Collections | Nein | Nein | Noch nie vollständig durchgeführt; Deep Research + Skripte können Prüfung übernehmen. |
| Chunking + 6 Linsen beibehalten | – | Ja (beibehalten) | G-Atlas-Direktive betraf Speichertrennung, nicht die Chunk-/Linsen-Logik. |

---

## 5. Referenzen

- **Optimierungsanweisung (Eichung):** `@CORE_EICHUNG.md` Anhang.
- **RAG/Vektorisierung:** `@docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md`; `src/db/multi_view_client.py`, `src/ai/model_registry.py`.
- **Deep Research Verifikation:** `@docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md`.
- **G-Atlas / Leidensdruck:** `src/core/Leidensdruck und Genese.md`; Stellen in `gemini.md` (duale Topologie, ChromaDB nur float).
