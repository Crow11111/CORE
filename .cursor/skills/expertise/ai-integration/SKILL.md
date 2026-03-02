---
name: expertise-ai-integration
description: Fachgebiet AI/LLM-Integration für Schicht-3-Produzenten. Prompt-Engineering, Embeddings, Triage, Model-Tiering. Ollama, Gemini, Bias Damper, TIE, AER.
---

# Expertise: AI/LLM-Integration

## Model-Tiering (ATLAS)

| Tier | Modell | Einsatz |
|------|--------|---------|
| 3/4 | Ollama (SLM) | Lokale, leichte Tasks |
| 5 | Gemini (Heavy) | Dev-Agent, Reasoning, WhatsApp |

## Kernkonzepte

- **Prompt-Engineering**: Klare Instruktionen, Few-Shot, System-Prompts
- **Embedding-Strategien**: Ein Modell pro Use-Case, Chunk-Größe passend
- **Triage-Routing**: Leichte Anfragen → SLM, komplexe → Heavy
- **RAG**: ChromaDB-Query → Kontext → LLM

## ATLAS-spezifisch

- **Bias Damper**: Confidence-Filter, Anti-Halluzination
- **TIE (Token Implosion)**: Komprimierte Darstellung
- **AER**: Architektur-Elemente für Reasoning
- **Gemini**: google-genai SDK, GEMINI_API_KEY aus .env
