# CORE INVENTORY REGISTER

**Vector:** 2210 (Sein) | 2201 (Denken)
**Status:** ACTIVE
**Zentrales Verwaltungsdokument für alle Systemkomponenten (Code & Dokumentation).**

---

## 1. DOKUMENTATIONS-INDEX

| Kategorie | Pfad | Funktion |
|-----------|------|----------|
| **Stammdokumente** | `docs/00_STAMMDOKUMENTE/` | Management Summary, Inventar, Einstiegspunkte. |
| **CORE DNA** | `docs/01_CORE_DNA/` | Verfassung, Axiome, 4-Strang-Architektur, Codex. |
| **Axiom 0** | `docs/01_CORE_DNA/AXIOM_0_AUTOPOIESIS.md` | Die Autopoiesis des Gitters (x^2=x+1). |
| **White Paper** | `docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md` | Theorie-Synthese & Topologie. |
| **Architektur** | `docs/02_ARCHITECTURE/` | System-Design, Schnittstellen, Flow-Diagramme. |
| **AI-Modelle** | `docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` | Modell-IDs, Rollen-Mapping, Kosten 2.5 Flash vs Pro, Token-Richtwerte, Deep Research & Computer Use. |
| **Deep Research & Computer Use** | `docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md` | Deep Research: Projekt-Omega-Verifikation (Vektorisierung, ChromaDB, Abgleich). Computer Use: Linux-Integration. |
| **Duale Topologie & Vektor-Härtung** | `docs/02_ARCHITECTURE/DUALE_TOPOLOGIE_UND_VEKTOR_HAERTUNG.md` | G-Atlas-Soll; Ist-Zustand; RAG-Einheitlichkeit; Vektor-Härtung. |
| **AI Studio Prompt** | `docs/02_ARCHITECTURE/AI_STUDIO_PROMPT.md` | Copy-Paste-Prompt für Google AI Studio (Schnittstellen, Live=Flash, Pro). |
| **Orchestrierung Linux** | `docs/02_ARCHITECTURE/OMEGA_LINUX_ORCHESTRATION.md` | Topologie Arch, Health-Skripte, Testmatrix. |
| **Jarvis ↔ OMEGA LLM** | `docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md` | Plasmoid Health-URL, falsche `/v1/chat/completions`-Basis, Kompat-Route `/v1/chat/completions/health`. |
| **ATLAS Ω Voice** | `docs/02_ARCHITECTURE/ATLAS_OMEGA_VOICE_PLASMOID.md` | KDE-Plasmoid `atlas-omega-voice/`, deutsch, OMEGA-Backend, `CORE_API_URL` per Umgebung. |
| **ATLAS Whisper-Setup** | `atlas-omega-voice/scripts/install_whisper_modell.sh` | Lädt `ggml-tiny.bin` nach `~/.local/share/jarvis/` für Wake-Wort (siehe ATLAS-Doku). |
| **Bibliothek Kern** | `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` | Zentraler Einstieg; Index 00–05, Was wurde gemacht, Wo nachschauen. |
| **Infrastruktur** | `docs/03_INFRASTRUCTURE/` | VPS-Setup, Docker-Sandbox, Backup-Pläne. |
| **VPS-Knoten & Flüsse** | `docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md` | Monica, Kong, Evolution, DBs: Zweck, Pull/Push-Matrix, Einbindung. |
| **Ollama VPS (Strang B)** | `docs/03_INFRASTRUCTURE/VPS_OLLAMA_SETUP.md` | Ollama auf Hostinger-VPS, Port 11434, Modell, Firewall. |
| **Vollkreis-Plan** | `docs/05_AUDIT_PLANNING/OMEGA_VOLLKREIS_PLAN.md` | Geschlossene Kette, Team-Arbeitspakete A–G, Linux-Auswirkungen. |
| **Prozesse** | `docs/04_PROCESSES/` | Workflows, Sicherheitsrat, Deployment-Regeln. |
| **sudoers OMEGA** | `docs/04_PROCESSES/SUDOERS_OMEGA_DAEMONS.md` | Vorlage `/etc/sudoers.d/` für NOPASSWD `systemctl` auf omega-* Units. |
| **Audit & Planung** | `docs/05_AUDIT_PLANNING/` | Session Logs, technische Schulden, Roadmaps. |
| **OC Brain Plan** | `docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md` | Vollständiger Plan Stränge A–E, Abnahme A1–A7. |
| **OC Brain Auftrag** | `docs/05_AUDIT_PLANNING/OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md` | Ausführungsauftrag an Team (alles umsetzen lassen). |
| **OC Brain RAG Spec** | `docs/02_ARCHITECTURE/OC_BRAIN_RAG_SPEC.md` | RAG-Pipeline Query → ChromaDB → Context → LLM (Strang D). |
| **OC Brain Strang A+E Bericht** | `docs/05_AUDIT_PLANNING/OC_BRAIN_STRANG_A_E_BERICHT.md` | Kurzbericht Diagnose (doctor) + WhatsApp (QR-Pairing, Config). |
| **OC Brain Strang B Bericht** | `docs/05_AUDIT_PLANNING/OC_BRAIN_STRANG_B_BERICHT.md` | Kurzbericht Ollama auf VPS (Installation, api/tags, Modell). |
| **Session-Log 2026-03-14** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-14.md` | Durchgeführte Schritte OC Brain (Verify, Doctor, Ollama), Abnahme A1–A7. |
| **Wissensbasis** | `docs/06_WORLD_KNOWLEDGE/` | Externe Forschung, Theorie-Cluster. |

---

## 2. SYSTEM-KOMPONENTEN (CODE)

### 2.1 Core Services (`src/`)
| Komponente | Pfad | Beschreibung |
|------------|------|--------------|
| **API Backend** | `src/api/` | FastAPI Server, Webhooks, Telemetrie-Endpunkte. |
| **Agent Pool** | `src/agents/` | Spezialisierte Agenten-Klassen (Core, Scout, etc.). |
| **Logic Core** | `src/logic_core/` | Takt-Gate, Gravitator, Veto-Logik, Filter. |
| **Crystal Engine** | `src/logic_core/crystal_grid_engine.py` | Topologisches Gitter-Snapping (Axiom 0). |
| **AI Interface** | `src/ai/` | LLM-Routing, ResilientLLMInterface, Prompt-Kompression. |
| **Model Registry** | `src/ai/model_registry.py` | Env-basierte Modell-IDs und Rollen-Mapping (siehe AI_MODEL_CAPABILITIES.md). |
| **API Inspector** | `src/ai/api_inspector.py` | list_gemini_models, list_ollama_models für Task-Router/Agenten. |
| **Network** | `src/network/` | Chroma-Client, OpenClaw-Client, HA-Connector. |
| **Voice** | `src/voice/` | TTS-Dispatcher, Smart-Command-Parser, Listener. |

### 2.2 Daemons & Scripts
| Typ | Pfad | Funktion |
|-----|------|----------|
| **Daemons** | `src/daemons/` | Watchdog, Event-Bus, Vision-Daemon. |
| **Scripts** | `src/scripts/` | Deployment-Skripte, Verifikationstools, Migrationen. |
| **Key Script** | `src/scripts/verify_core_integrity.py` | Validiert die Integrität des Gesamtsystems. |
| **Key Script** | `src/scripts/daily_backup.py` | Automatisiertes Backup-System. |
| **Key Script** | `src/scripts/setup_vps_hostinger.py` | Initiales Server-Setup. |
| **Key Script** | `src/scripts/verify_oc_brain_deliverables.py` | Abnahme OC Brain Plan (Verify, don't trust). |
| **Key Script** | `src/scripts/install_ollama_vps.py` | Strang B: Ollama auf VPS installieren, Modell pullen, api/tags prüfen. |
| **Key Script** | `src/scripts/ingest_mth_profile_to_chroma.py` | MTH-Profil Tiefen-Chunking → ChromaDB mth_user_profile. |
| **Key Script** | `src/scripts/verify_vps_stack.py` | VPS: SSH, docker ps, Chroma v2 heartbeat; optionale Knoten Evolution, Monica, Kong (siehe VPS_KNOTEN_UND_FLUSSE). |
| **Utils** | `src/utils/` | Circuit-Breaker, Zeit-Metriken, Logging-Helfer. |

---

## 3. INFRASTRUKTUR & DEPLOYMENT

### 3.1 Docker-Container
| Container | Pfad | Rolle |
|-----------|------|-------|
| **OpenClaw** | `docker/openclaw-admin/` | Messenger-Gateway (VPS). |
| **Scout** | `docker/scout/` | Edge-Compute-Layer (Pi). |
| **AGI-State** | `docker/agi-state/` | Persistenter Systemzustand. |

### 3.2 Konfiguration
| Datei | Funktion |
|-------|----------|
| `.env` | Zentrale Umgebungsvariablen (Keys, Ports, Hosts). |
| `.cursorrules` | Primäre operative Direktiven für Agenten. |
| `src/config/core_state.py` | Mathematischer Kern (State Vector, Axiome). |

---

## 4. DATA & MODELS
| Typ | Pfad | Beschreibung |
|-----|------|--------------|
| **ChromaDB** | `data/chroma_db/` | Lokaler Vector-Store (Failover). |
| **WakeWords** | `models/wakeword_mtho/` | Trainierte Modelle für "Hey CORE". |
| **Logdateien** | `logs/` | System- und Audit-Logs. |

---

## REGEL: INVENTAR-PFLICHT
1. Jede neue Datei (Skript oder Dokument) MUSS unmittelbar in diesem Register nachgetragen werden.
2. Bei Umbenennung oder Löschung ist das Register simultan zu aktualisieren.
3. Der `DOCS_INDEX.md` referenziert dieses Dokument als Master-Liste.
