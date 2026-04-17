# SKILL-BASED ORCHESTRATION V2

**Vector:** 2210 | **Delta:** 0.049
**Status:** ACTIVE
**Zugehörigkeit:** CORE-AI-ORCHESTRATION

## 1. ÜBERSICHT
Die Skill-basierte Orchestrierung V2 (SBOv2) ist das zentrale Nervensystem der OMEGA-Intelligenz. Sie ermöglicht eine dynamische Allokation von Rechenleistung und spezialisierter Intelligenz basierend auf der Komplexität der Anfrage. Anstatt ein "One-Size-Fits-All"-Modell zu nutzen, wird jede Anfrage durch eine Triage-Schicht (Ring 0) analysiert und an den optimalen "Skill-Worker" delegiert.

## 2. DIE 4 KERN-SKILLS

| Skill | Modell / Engine | Fokus |
|-------|-----------------|-------|
| **Wiki Expert** | Claude Code (Local) | Tiefe Extraktion aus dem OMEGA-Kanon, Axiom-Validierung, Theorie-Abgleich. |
| **Heavy Reasoner** | Gemini 3.1 Pro | Komplexe Architektur-Entscheidungen, Multi-File Refactoring, logische Ketten-Analysen. |
| **Simple Coder** | Gemini 3.1 Flash Lite | Standard-Coding, Unit-Tests, Dokumentations-Updates, einfache API-Integrationen. |
| **Stupid Coder** | Gemma 4 (Dreadnought) | Repetitive Aufgaben, lokale Skript-Ausführung, Smart-Home-Befehle, Fallback bei Cloud-Ausfall. |

### 2.1 Wiki Expert (OMEGA LLM-Wiki)
Der Wiki Expert ist eine spezialisierte Instanz, die direkten Zugriff auf das `OMEGA_WIKI` Verzeichnis hat.
- **Integration:** Erfolgt via `Claude Code` CLI.
- **Prozess:** Der Orchestrator ruft im Verzeichnis `/home/mth/OMEGA_WIKI` den Befehl `claude -p "..."` auf.
- **Vorteil:** Claude fungiert hier als "Reasoning-Indexer", der über alle Markdown-Dokumente des Kanons hinweg Zusammenhänge erkennt, ohne dass ein vollständiger RAG-Overhead notwendig ist.

### 2.2 Stupid Coder (Dreadnought Primat)
Dieser Skill repräsentiert die lokale Autarkie.
- **Hardware:** Erfordert die **Dreadnought GPU** (minimale Latenz, hohe Bandbreite) für den Betrieb von **Gemma 4**.
- **Sicherheits-Layer:** Führt Code lokal aus, wenn Cloud-Modelle aufgrund von Sicherheits-Vetos oder Netzstörungen nicht verfügbar sind.

## 3. TRIAGE & ROUTING (RING 0)
Die Triage erfolgt semantisch. Ein "Fast Path" erkennt bekannte Keywords (z.B. Home-Control), während ein LLM-Triage-Modell (Gemini 3.1 Flash Lite) die komplexeren Intents klassifiziert.

### CAR/CDR BALANCE
- **CAR (Structure):** Die `ResilientLLMInterface` Klasse in `src/ai/llm_interface.py`.
- **CDR (Content):** Die dynamischen Prompts und die Modell-Registry in `src/ai/model_registry.py`.

## 4. HARDWARE-ANFORDERUNGEN
Um die volle Performance der SBOv2 zu gewährleisten, ist folgende Hardware-Konfiguration (Dreadnought-Klasse) zwingend:
- **GPU:** NVIDIA RTX 5090 oder vergleichbar (für Gemma 4 31B/70B Real-Time Inference).
- **Inferenz-Engine:** Ollama (lokal) mit optimierten GGUF-Quants.
- **Konnektivität:** Low-Latency mTLS-Proxy zum VPS für Remote-Abfragen.
