# AI-Modell-Capabilities (CORE/OMEGA)

**Vektor:** 2210 | 2201 | Delta 0.049
**Zweck:** Einzige Referenz für verfügbare Modelle, APIs und rollenbasierte Zuordnung. Alle Agenten und Daemons beziehen Modellwahl und Token-Budgets von hier bzw. von `src/ai/model_registry.py`.

---

## 1. Aus .env und Code extrahierte Modelle

### Gemini (Google)

| Modell-ID | Verwendung in CORE | Aufgaben | Kostenklasse |
|-----------|---------------------|----------|--------------|
| `gemini-3.1-pro-preview` | GEMINI_DEV_AGENT_MODEL, GEMINI_HEAVY_MODEL; WhatsApp-Audio, TTS/STT, Vision (Brio), Deploy OC | Deep Reasoning, Audio, Vision | Hoch |
| `gemini-3.1-flash-preview` | OC Brain / Deploy | Schnelle Antworten, Tools | Mittel |
| `gemini-3-pro-preview` | Fallback Vision, Transcribe-Skripte | Vision, Transkription | Mittel |
| `gemini-2.5-flash` | Dictate-Route (STT) | STT, kurze Latenz | Niedrig |
| `gemini-2.5-pro` | Transcribe-Batch Fallback | STT, längere Texte | Mittel |
| `gemini-2.0-flash-exp` | core_vision_daemon | Vision (Schnell) | Niedrig |
| `gemini-embedding-001` | multi_view_client (Embeddings), Registry Rolle „embedding“ | RAG/Vektorisierung | Niedrig |

**RAG / Vektorisierung (multimodal angebunden):** Das Embedding-Modell fuer RAG ist zentral ueber `src/ai/model_registry.py` (Rolle `embedding`) und optional `.env` `GEMINI_EMBED_MODEL` konfigurierbar. Alle Vektorisierungs-Pfade (Multi-View 6-Linsen, ingest_core_documents, pgvector multi_view_embeddings) nutzen dieses Modell. Fallback: Ollama `nomic-embed-text`. Damit ist das multimodale RAG-Modell fuer die Vektorisierung verbindlich angebunden.

**Spezialisierte Modelle (Auswahl, z. B. in Cursor/API sichtbar):**
| Modell-ID | Zweck | CORE-Nutzung |
|-----------|--------|----------------|
| `gemini-2.5-flash-preview-tts` | TTS (Text→Sprache) | gemini_tts.py (Kore, Health Board „Kore vorlesen“) |
| `gemini-2.5-pro-preview-tts` | TTS Pro (hoehere Qualitaet) | Optional per GEMINI_TTS_MODEL |
| `gemini-embedding-2-preview` | Embedding (neuer) | Optional statt embedding-001 |
| **STT (Diktat):** Kein eigenes Spezialmodell in der Liste – STT laeuft ueber Multimodal (Audio→Text) mit `gemini-2.5-flash` bzw. `gemini-2.5-pro`. |

**Kosten 2.5 Flash vs 2.5 Pro (Richtwerte, API):**
| Modell | Input (pro 1M Tokens) | Output (pro 1M Tokens) | Hinweis |
|--------|------------------------|-------------------------|---------|
| **gemini-2.5-flash** | ca. 0,30 USD | ca. 2,50 USD | Beste Kosten/Leistung; STT, Diktat, schnelle Tasks. |
| **gemini-2.5-pro** | ca. 1,25 USD (≤200K Kontext) | ca. 10,00 USD | Komplexes Reasoning, großer Kontext; >200K: ca. 2,50 / 15,00 USD. |
| **Unterschied** | Pro ca. **4× teurer** (Input) | Pro ca. **4× teurer** (Output) | Flash für Latenz/kostenbewusst; Pro für Tiefe und Kontext. |

**Sprachschnittstelle (Dictate / STT mit 2.5 Flash) – Token und Kosten (Richtwerte):**
- Pro Diktat-Request: Audio (Input) wird von der API oft als aequivalent zu Tokens berechnet; typisch ca. 1–2 Min. Audio ≈ grob 500–1500 Token-Aequivalent (Input). Output: Transkript, oft 50–300 Tokens pro Aufnahme.
- **Kosten 2.5 Flash:** Input ca. 0,30 USD/1M, Output ca. 2,50 USD/1M.
- **Beispiel Monat:** 100 Diktate à ~1000 Input + 150 Output → 100k Input, 15k Output → ca. 0,03 + 0,04 ≈ **0,07 USD**. 500 Diktate → ca. **0,35–0,50 USD/Monat**. (Exakte Audio-Preise in der Google-Dokumentation pruefen; manche Tarife rechnen Audio nach Dauer.)

**API:** `google-genai` (genai.Client), REST generativelanguage.googleapis.com. Model Discovery: `genai.list_models()` bzw. API-Dokumentation nutzen.

### Anthropic (Claude)

| Modell-ID | .env | Verwendung | Aufgaben |
|-----------|------|------------|----------|
| `claude-opus-4-6` | ANTHROPIC_HEAVY_MODEL | Schwere Analysen, Audit | Deep Reasoning, Council |
| `claude-sonnet-4-6` | ANTHROPIC_FAST_MODEL | Schnelle strukturierte Antworten | Triage, Code-Review |

**API:** `anthropic`, `langchain-anthropic`. Keys: ANTHROPIC_API_KEY / ANTHROPIC_API_KEY_CLOUD.

### Ollama (lokal / Scout / VPS)

| Modell | Ort | .env | Verwendung |
|--------|-----|------|------------|
| `llama3.2:1b` | Scout (OLLAMA_HOST) | OLLAMA_MODEL | Triage (core_llm), ResilientLLM L2 |
| `llama3.1:latest` | Dreadnought (OLLAMA_LOCAL_HOST) | OLLAMA_HEAVY_MODEL | ResilientLLM L3 Fallback |
| `qwen2.5:7b` | VPS (install_ollama_vps) | – | OC Brain, OpenClaw |
| `nomic-embed-text` | Lokal/Scout | – | Embedding-Fallback (multi_view_client) |

**API:** `langchain_ollama.ChatOllama`, HTTP `OLLAMA_HOST:11434` (api/tags, api/generate).

### Nexos

| Modell | .env | Verwendung |
|--------|------|------------|
| NEXOS_DEFAULT_MODEL (UUID) | NEXOS_BASE_URL, NEXOS_API_KEY | Optional, externe API |

---

## 2. Rollen-Mapping (Agenten / Daemons)

| Rolle | Primär | Fallback | Typische Aufgaben | Token-Budget (Richtwert) |
|-------|--------|----------|--------------------|---------------------------|
| **CEO/Orchestrator** | Opus 4.6 (Cursor) | – | Planung, Audit, Delegation | Nach Kontext |
| **Triage (Intent)** | Ollama llama3.2:1b (Scout) | – | command / deep_reasoning / chat | &lt; 1k |
| **Heavy (Chat/Reasoning)** | VPS OpenClaw → Gemini 3.1 Pro | Scout Ollama → Local Ollama | Antworten, Analyse | &lt; 8k |
| **WhatsApp Audio** | gemini-3.1-pro-preview | – | Transkription, Analyse | Nach Länge |
| **Dictate (STT)** | gemini-2.5-pro (Default) | gemini-2.5-flash (Live) | Semantik (Pro); Live-Pingpong = Flash; `/api/dictate?mode=live` | &lt; 2k |
| **Vision (Daemon)** | gemini-2.0-flash-exp | – | Snapshot-Analyse | &lt; 2k |
| **Embedding** | gemini-embedding-001 | Ollama nomic-embed-text | Vektoren | – |
| **OC Brain / OpenClaw** | google/gemini-3.1-pro-preview, Ollama qwen2.5:7b | – | Chat, Tools auf VPS | Nach Konfiguration |

---

## 3. API-Clients und Discovery

- **Gemini:** `from google import genai` → `genai.Client(api_key=...)`; Modellliste über offizielle Model-API (Discovery) abfragbar.
- **Anthropic:** `anthropic.Anthropic(api_key=...)`; Modellliste in Doku.
- **Ollama:** `GET {OLLAMA_HOST}/api/tags` → Liste der gepullten Modelle.

Ein zentrales Modul `src/ai/api_inspector.py` kann bei Bedarf diese Quellen abfragen und für Task-Router/Agenten bereitstellen.

---

## 4. Deep Research & Computer Use (Gemini)

Beide Fähigkeiten sind für CORE/Projekt Omega relevant: **Deep Research** für prüfende/verifizierende Aufgaben (Vektorisierung, DB-Abgleich, ChromaDB); **Computer Use** für tiefere Linux-Integration (UI-Automation, Browser, Terminal).

### 4.1 Deep Research

- **API/Modell:** Gemini Deep Research (z. B. `deep-research-pro-preview-12-2025`), erreichbar u. a. über die **Interactions API** (asynchron, langer Kontext).
- **Einsatz in CORE:** Projekt-Omega-Prüfung: Sicherstellen, dass **Textverarbeitung**, **Vektorisierung**, **Datenbank-Abgleich**, **ChromaDB-Einlesen** und **Vektor-Abgleich** (lokal vs. VPS, Konsistenz) stattfinden. Deep Research kann Dokumentation und Codebase durchsuchen, Abläufe prüfen und Berichte mit Quellen liefern.
- **Konkret:** Vor Abnahme/Vollkreis: Deep Research mit Auftrag „Prüfe Projekt Omega: Vektorisierungspfade, ChromaDB-Collections, Abgleich Vektor-DB, Multi-View-Ingest, Registry-Embedding-Anbindung“ – Ergebnis als verifizierender Report.
- **Dokumentation:** Siehe `@docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md` (Checkliste Verifikation, Einbindung).

### 4.2 Computer Use

- **API/Modell:** Gemini 2.5 Computer Use (z. B. `gemini-2.5-computer-use-preview-10-2025`): UI-Interaktion, Browser-Automation, Multi-Step-Software-Tasks. Basiert auf 2.5 Pro Vision.
- **Einsatz in CORE:** „Dich tiefer in Linux reinkriegen“ – Automatisierung von Terminal, Fenstersteuerung, Cockpit-Interaktion, Skript-Ausführung aus einem Agenten-Handling heraus. Perspektive: Computer Use als Kanal für CORE auf Dreadnought (Arch) für wiederholbare, UI-/OS-nahe Schritte.
- **Dokumentation:** Siehe `@docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md` (Linux-Integration, geplante Nutzung).

---

## 5. Referenzen

- Konfiguration: `.env` (GEMINI_*, ANTHROPIC_*, OLLAMA_*, NEXOS_*).
- Code: `src/ai/llm_interface.py`, `src/ai/model_registry.py` (Rolle `embedding`), `src/ai/whatsapp_audio_processor.py`, `src/api/routes/dictate.py`, `src/daemons/core_vision_daemon.py`, `src/db/multi_view_client.py` (RAG-Vektorisierung an Registry).
- Deep Research & Computer Use: `@docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md`.
- BIBLIOTHEK: `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` (Regel: Immer einbinden).


[LEGACY_UNAUDITED]
