# Deep Research & Computer Use (CORE/Projekt Omega)

**Vektor:** 2210 | 2201 | Delta 0.049
**Zweck:** Nutzung von Gemini Deep Research für Projekt-Omega-Verifikation (Vektorisierung, ChromaDB, Abgleich) und von Computer Use für tiefere Linux-Integration. Referenz: `@docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` §4.

---

## 1. Deep Research – Projekt-Omega-Verifikation

Deep Research eignet sich dafür, **prüfend** zu bestätigen, dass im Projekt Omega die folgenden Schritte und Systeme konsistent laufen:

### 1.1 Checkliste: Was Deep Research prüfen soll

| Prüfpunkt | Beschreibung | Wo nachschauen / messbar |
|-----------|--------------|---------------------------|
| **Textverarbeitung** | Texte werden korrekt gelesen, gechunkt und für RAG vorbereitet. | `ingest_core_documents.py`, Chunk-Logik; Multi-View-Linsen. |
| **Vektorisierung** | Embedding-Modell aus Registry; alle Ingest-Pfade nutzen dasselbe Modell. | `src/db/multi_view_client.py` → `get_model_for_role("embedding")`; `model_registry.EMBED_MODEL`. |
| **Datenbank-Abgleich** | Vektor-DB (ChromaDB lokal/VPS, pgvector multi_view_embeddings) sind konsistent mit Konfiguration. | `verify_vps_stack.py`, Chroma heartbeat; `run_vollkreis_abnahme.py`. |
| **ChromaDB einlesen** | Collections (core_directives, session_logs, knowledge_graph, …) sind erreichbar und werden von Gravitator/Context-Injector genutzt. | `src/network/chroma_client.py`; `chroma_audit.py`; VPS Chroma v2 API. |
| **Vektoren abgleichen** | Keine Bruchstellen zwischen lokalem Embedding und VPS-Chroma; gleiche Dimension (z. B. 768 für Gemini). | Multi-View 768 dim; Chroma Collections Dimension; Sync-Skripte (z. B. `sync_core_directives_to_vps`, `migrate_chroma_to_vps`). |

### 1.2 Typischer Deep-Research-Auftrag (Formulierung)

> „Prüfe Projekt Omega: (1) Welche Pfade verarbeiten Texte und erzeugen Vektoren? (2) Ist die Vektorisierung an die Model Registry (Rolle embedding) angebunden? (3) Wo wird ChromaDB gelesen/geschrieben und wie ist der Abgleich zwischen lokaler und VPS Vektor-DB? (4) Laufen ChromaDB-Einlesen und Vektor-Abgleich konsistent (Dimension, Collections, Ingest-Skripte)? Liefer einen kurzen Report mit Quellen.“

### 1.3 Einbindung in den Ablauf

- **Vor Vollkreis-Abnahme:** Deep Research als zusätzliche, prüfende Instanz (neben `run_vollkreis_abnahme.py` und manueller Prüfung).
- **API:** Gemini Deep Research über Interactions API / Google AI Studio (asynchron; Ergebnis als Report mit Zitaten).
- **Output:** Report in Session-Log oder unter `docs/05_AUDIT_PLANNING/` ablegen (z. B. `DEEP_RESEARCH_OMEGA_VERIFIKATION_<Datum>.md`).

---

## 2. Computer Use – Linux-Integration

Computer Use ermöglicht es, einen Agenten (Gemini 2.5 Computer Use) **UI und System** bedienen zu lassen: Browser, Terminal, Fenstersteuerung. Für CORE bedeutet das:

### 2.1 Ziel: „Dich tiefer in Linux reinkriegen“

- **Dreadnought (Arch):** Wiederholbare Schritte wie Cockpit öffnen, Skripte starten, Logs prüfen, systemd-Status abfragen – perspektivisch über Computer Use steuerbar.
- **Konkret:** Modell erhält Screenshot/UI-State und kann Aktionen vorschlagen oder ausführen (je nach API-Features: Klicks, Tastatur, Terminal-Befehle). So wird CORE nicht nur über API, sondern auch über die reale Nutzeroberfläche und das OS angebunden.

### 2.2 Geplante Nutzung (Überblick)

| Bereich | Nutzung |
|---------|---------|
| **Cockpit / Frontend** | Automatisierte Prüfung oder Bedienung des OMEGA-Cockpits (z. B. Health Board, Diktat, Status). |
| **Terminal / Skripte** | Ausführung und Prüfung von Skripten (`run_vollkreis_abnahme.py`, `verify_vps_stack.py`, `chroma_audit.py`) in einer kontrollierten Umgebung. |
| **systemd / Dienste** | Status-Checks (omega-backend, omega-frontend, Daemons) als Teil eines verifizierenden Workflows. |

### 2.3 Technik & Referenz

- **Modell:** z. B. `gemini-2.5-computer-use-preview-10-2025` (Gemini API).
- **Dokumentation:** [Gemini 2.5 Computer Use model | Gemini API | Google AI for Developers](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-computer-use-preview-10-2025); ggf. Interactions API für längere Sessions.
- **Sicherheit:** Computer Use nur in abgegrenzter Umgebung (z. B. Dev-Modus, bestimmte Fenster/Anwendungen); keine sensiblen Credentials im sichtbaren Kontext.

---

## 3. Referenzen

- **Modelle & Kosten:** `@docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` (§1 Kosten 2.5 Flash vs Pro, §4 Deep Research & Computer Use).
- **Duale Topologie & Vektor-Härtung:** `@docs/02_ARCHITECTURE/DUALE_TOPOLOGIE_UND_VEKTOR_HAERTUNG.md` (G-Atlas-Soll, Ist-Zustand ChromaDB/PG, Härtungsstatus, Chunking/Multi-View).
- **Vollkreis & Abnahme:** `@docs/05_AUDIT_PLANNING/OMEGA_VOLLKREIS_PLAN.md`; `run_vollkreis_abnahme.py`.
- **RAG/Vektorisierung:** `@docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` (RAG/Vektorisierung); `src/db/multi_view_client.py`, `src/ai/model_registry.py`.
- **BIBLIOTHEK:** `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md`.
