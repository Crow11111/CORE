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
| `gemini-embedding-001` | multi_view_client (Embeddings) | Embedding | Niedrig |

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
| **Dictate (STT)** | gemini-2.5-flash | – | Kurze Latenz STT | &lt; 2k |
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

## 4. Referenzen

- Konfiguration: `.env` (GEMINI_*, ANTHROPIC_*, OLLAMA_*, NEXOS_*).
- Code: `src/ai/llm_interface.py`, `src/ai/whatsapp_audio_processor.py`, `src/api/routes/dictate.py`, `src/daemons/core_vision_daemon.py`, `src/db/multi_view_client.py`.
- BIBLIOTHEK: `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` (Regel: Immer einbinden).
