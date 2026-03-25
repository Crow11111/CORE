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
| **DNA-Archiv (Legacy Genesis)** | `docs/01_CORE_DNA/_archive/` | Historischer Genesis-/Tesserakt-Text ohne Kanon-Status; Stub: `CORE_GENESIS_FINAL_ARCHIVE.md`. |
| **Genesis-Stub (Link-Anker)** | `docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md` | Obsolet-Hinweis; verweist auf SYSTEM_CODEX, Bibliothek, `_archive/`. |
| **Genesis-Weiterleitung (Root docs/)** | `docs/CORE_GENESIS_FINAL_ARCHIVE.md` | Kurze Weiterleitung auf Stub/Archiv. |
| **Axiom 0** | `docs/01_CORE_DNA/AXIOM_0_AUTOPOIESIS.md` | Die Autopoiesis des Gitters (x^2=x+1). |
| **White Paper** | `docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md` | Theorie-Synthese & Topologie (Kurzfassung). |
| **White Paper vollständig** | `docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION_VOLLSTANDIG.md` | Herleitungs-Ausgabe: Ω_b, x=x-Kaskade, MRI, Teil F Konsolidierung. |
| **Whitepaper 5D (Split)** | `docs/01_CORE_DNA/5d/WHITEPAPER/` | Kapitel I–IV + Vollständig; `README.md` → NotebookLM-Workflow. |
| **Whitepaper II (Escape)** | `docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_II_OMEGA_Escape_Vector.md` | Die OMEGA-Escape-Vector Theorie, Pi/Phi Dualität, Holographische 2D-Faltung. |
| **Formel Cheat-Sheet** | `docs/01_CORE_DNA/CORE_FORMELN_CHEAT_SHEET.md` | Zentrale Anlaufstelle für OMEGA-Gleichungen: MRI-Dynamo, Symbiose-Antrieb, Kardanischer Fixpunkt. |
| **Rat der Titanen R2** | `docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/` | Ollama-Gutachten (`run_omega_science_council_r2.py`) zur ausformulierten Datei. |
| **Colab Science Council** | `docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/science_council_colab.ipynb` | Jupyter Notebook für Google Colab (GPU-Laufzeit). |
| **Colab Guide** | `docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/COLAB_SCIENCE_COUNCIL.md` | Schritt-für-Schritt Anleitung für Colab. |
| **Whitepaper NotebookLM** | `docs/01_CORE_DNA/5d/WHITEPAPER_NOTEBOOKLM/` | Sanitized Markdown für NotebookLM (`whitepaper_for_notebooklm.py`). |
| **Architektur** | `docs/02_ARCHITECTURE/` | System-Design, Schnittstellen, Flow-Diagramme. |
| **OpenClaw Membran** | `docs/02_ARCHITECTURE/OPENCLAW_MEMBRAN_TESSERAKT.md` | Blueprint: Facetten-Atomisierung, isolierte Räume, kreuz-modale Konvergenz, Entkopplung. |
| **Landkarte Clients / Knoten** | `docs/02_ARCHITECTURE/LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` | Überblick: KI-Clients vs. CORE-Backend vs. VPS; Push/Pull; geschlossene Kreise; Verweise auf VPS_KNOTEN, SCHNITTSTELLEN, G_CORE_CIRCLE. |
| **AI-Modelle** | `docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` | Modell-IDs, Rollen-Mapping, Kosten 2.5 Flash vs Pro, Token-Richtwerte, Deep Research & Computer Use. |
| **Deep Research & Computer Use** | `docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md` | Deep Research: Projekt-Omega-Verifikation (Vektorisierung, ChromaDB, Abgleich). Computer Use: Linux-Integration. |
| **Duale Topologie & Vektor-Härtung** | `docs/02_ARCHITECTURE/DUALE_TOPOLOGIE_UND_VEKTOR_HAERTUNG.md` | G-Atlas-Soll; Ist-Zustand; RAG-Einheitlichkeit; Vektor-Härtung. |
| **AI Studio Prompt** | `docs/02_ARCHITECTURE/AI_STUDIO_PROMPT.md` | Copy-Paste-Prompt für Google AI Studio (Schnittstellen, Live=Flash, Pro). |
| **Orchestrierung Linux** | `docs/02_ARCHITECTURE/OMEGA_LINUX_ORCHESTRATION.md` | Topologie Arch, Health-Skripte, Testmatrix. |
| **WhatsApp Closed-Loop** | `docs/02_ARCHITECTURE/WHATSAPP_CLOSED_LOOP_OC_ADMIN.md` | WhatsApp Push-and-Pull Logik; OC Brain als Admin; 5-Phase Engine Loop (Takt 1-4); Traceability. |
| **Jarvis ↔ OMEGA LLM** | `docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md` | Plasmoid Health-URL, falsche `/v1/chat/completions`-Basis, Kompat-Route `/v1/chat/completions/health`. |
| **ATLAS Ω Voice** | `docs/02_ARCHITECTURE/ATLAS_OMEGA_VOICE_PLASMOID.md` | KDE-Plasmoid `atlas-omega-voice/`, deutsch, OMEGA-Backend, `CORE_API_URL` per Umgebung. |
| **ATLAS Whisper-Setup** | `atlas-omega-voice/scripts/install_whisper_modell.sh` | Lädt `ggml-tiny.bin` nach `~/.local/share/jarvis/` für Wake-Wort (siehe ATLAS-Doku). |
| **ATLAS Piper-Stimme** | `atlas-omega-voice/scripts/install_piper_stimme.sh` | Lädt Piper-ONNX nach `~/.local/share/jarvis/piper-voices/` (Alan/Thorsten). |
| **ATLAS Legacy-Plasmoids** | `atlas-omega-voice/scripts/alte_plasmoids_auslagern.sh` | Archiviert Flex.Hub / lokales jarvis nach `~/.local/share/OMEGA-plasmoid-archiv/` (nicht unter `plasmoids/`); ruft Config-Bereinigung auf. |
| **ATLAS Plasma Leiste** | `atlas-omega-voice/scripts/plasma_entferne_flex_hub_applet.py` | Entfernt Applets per `plugin=` (Args, Default: Flex.Hub), z. B. `org.kde.plasma.activitypager` bei kaputtem `plasma-desktop`. |
| **Bibliothek Kern** | `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` | Zentraler Einstieg; Index 00–05, Operator-Todo (MCP/Extensions), Was wurde gemacht, Wo nachschauen. |
| **Kanonischer Einstieg** | `KANON_EINSTIEG.md` | Eine Tür: Tabelle „welche Frage → welche Datei“; Abgrenzung Megadatei vs. Index; Pflege-Regeln. |
| **DOCS_INDEX (thematisch)** | `docs/DOCS_INDEX.md` | Ordnerübersicht; ergänzend zu KANON/Bibliothek. |
| **CoolerControl Setup** | `docs/03_INFRASTRUCTURE/COOLER_CONTROL_SETUP.md` | Lüftersteuerung (it87), Silent-Profile, Gigabyte B560M. |
| **OS Audio Dictation** | `docs/04_PROCESSES/OS_AUDIO_DICTATION.md` | Headless Start/Stop Diktat-Workflow, Clipboard-Integration. |
| **Infrastruktur-Master (Root-Stub)** | `docs/00_CORE_INFRASTRUCTURE_MASTER.md` | Weiterleitung nach `00_STAMMDOKUMENTE/00_CORE_INFRASTRUCTURE_MASTER.md` (kanonischer Volltext). |
| **Infrastruktur** | `docs/03_INFRASTRUCTURE/` | VPS-Setup, Docker-Sandbox, Backup-Pläne. |
| **VPS-Knoten & Flüsse** | `docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md` | Monica, Kong, Evolution, DBs: Zweck, Pull/Push-Matrix, Einbindung. |
| **Ollama VPS (Strang B)** | `docs/03_INFRASTRUCTURE/VPS_OLLAMA_SETUP.md` | Ollama auf Hostinger-VPS, Port 11434, Modell, Firewall. |
| **Vollkreis-Plan** | `docs/05_AUDIT_PLANNING/OMEGA_VOLLKREIS_PLAN.md` | Geschlossene Kette, Team-Arbeitspakete A–G, Linux-Auswirkungen. |
| **Prozesse** | `docs/04_PROCESSES/` | Workflows, Sicherheitsrat, Deployment-Regeln. |
| **sudoers OMEGA** | `docs/04_PROCESSES/SUDOERS_OMEGA_DAEMONS.md` | Vorlage `/etc/sudoers.d/` für NOPASSWD `systemctl` auf omega-* Units. |
| **Audit & Planung** | `docs/05_AUDIT_PLANNING/` | Session Logs, technische Schulden, Roadmaps. |
| **Agent Refactor Plan** | `docs/05_AUDIT_PLANNING/AGENT_REFACTOR_PLAN.md` | Audit-Bericht und V2-Konzept für das Agenten-System (Schichten, Model-Zwang, MDC-Globs). |
| **OC Brain Plan** | `docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md` | Vollständiger Plan Stränge A–E, Abnahme A1–A7. |
| **OC Brain Auftrag** | `docs/05_AUDIT_PLANNING/OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md` | Ausführungsauftrag an Team (alles umsetzen lassen). |
| **OC Brain RAG Spec** | `docs/02_ARCHITECTURE/OC_BRAIN_RAG_SPEC.md` | RAG-Pipeline Query → ChromaDB → Context → LLM (Strang D). |
| **OC Brain Strang A+E Bericht** | `docs/05_AUDIT_PLANNING/OC_BRAIN_STRANG_A_E_BERICHT.md` | Kurzbericht Diagnose (doctor) + WhatsApp (QR-Pairing, Config). |
| **OC Brain Strang B Bericht** | `docs/05_AUDIT_PLANNING/OC_BRAIN_STRANG_B_BERICHT.md` | Kurzbericht Ollama auf VPS (Installation, api/tags, Modell). |
| **Projektplan ATLAS 2026** | `docs/05_AUDIT_PLANNING/PROJECT_PLAN_ATLAS_TRANSFORMATION_2026.md` | Detaillierter Plan (Luminescence, Sentinel, Memory-Core). |
| **Session-Log 2026-03-25 (Thermal/OS)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-25_THERMAL_AND_OS_FIXES.md` | Lüftersteuerung (it87), ACPI Standby Fix, Chrome Graceful Exit, Headless Audio Dictation. |
| **Session-Log 2026-03-25 (Agent Audit)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-25_AGENT_AUDIT.md` | Audit-Bericht "Full Service Agentur" und V2 Architektur-Plan. |
| **Session-Log 2026-03-24 (Kardan)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-24_KARDANIC_FOLD.md` | Kardanische Faltung (Complex -> 2x Float), Atlas-Härtung (Signal-Skepticism), ChromaDB-Eichung. |
| **Session-Log 2026-03-22 (Audio)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-22_AUDIO_REPAIR.md` | SIGNAL-COMMANDER: Reparatur Aufnahmekette (pw-record, Razer Seiren V3 Mini, RMS-Validierung). |
| **Session-Log 2026-03-21 (NotebookLM WP)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-21_NOTEBOOKLM_WHITEPAPER.md` | Whitepaper 5d → NotebookLM: Sanitizer, SGML-/Zeilenlängen-Fix, Inventar/Bibliothek. |
| **Session-Log 2026-03-20** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-20.md` | ATLAS Transformation (Red Theme, Daemon Monitoring, Deep RAG). |
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
| **Resonanz-Membran S↔P** | `src/logic_core/resonance_membrane.py` | float-Resonanz vs. int-Infrastruktur; `DualMembraneVector`; Entry-Adapter (WhatsApp `audio_seconds`); `omega_core` importiert dieselbe Klasse. |
| **AI Interface** | `src/ai/` | LLM-Routing, ResilientLLMInterface, Prompt-Kompression. |
| **Model Registry** | `src/ai/model_registry.py` | Env-basierte Modell-IDs und Rollen-Mapping (siehe AI_MODEL_CAPABILITIES.md). |
| **API Inspector** | `src/ai/api_inspector.py` | list_gemini_models, list_ollama_models für Task-Router/Agenten. |
| **Network** | `src/network/` | Chroma-Client, OpenClaw-Client, HA-Connector. |
| **Voice** | `src/voice/` | TTS-Dispatcher, Smart-Command-Parser, Listener. |

### 2.2 Root-Demonstratoren (außerhalb `src/`)
| Typ | Pfad | Funktion |
|-----|------|----------|
| **omega_core (Kardan-Anker)** | `omega_core.py` | Deterministische Mini-Kaskade; Abnahme: **`run_vollkreis_abnahme.py`** Block **Gk**. Verknüpfung Theorie ↔ ausgeführter Check; Doku: `KANON_EINSTIEG.md`. |

### 2.3 Daemons & Scripts
| Typ | Pfad | Funktion |
|-----|------|----------|
| **Daemons** | `src/daemons/` | Watchdog, Event-Bus, Vision-Daemon. |
| **Scripts** | `src/scripts/` | Deployment-Skripte, Verifikationstools, Migrationen. |
| **Key Script** | `src/scripts/ensure_kardanic_collections.py` | ChromaDB-Dimensionseichung (6144 dim) für kardanische Faltung. |
| **Key Script** | `src/scripts/verify_core_integrity.py` | Genesis-Audit (`src.core.Core`); **Aufruf nur von Repo-Root**, Exit 0/1. |
| **Key Script** | `src/scripts/daily_backup.py` | Automatisiertes Backup-System. |
| **Key Script** | `src/scripts/setup_vps_hostinger.py` | Initiales Server-Setup. |
| **Key Script** | `src/scripts/verify_oc_brain_deliverables.py` | Abnahme OC Brain Plan (Verify, don't trust). |
| **Key Script** | `src/scripts/install_ollama_vps.py` | Strang B: Ollama auf VPS installieren, Modell pullen, api/tags prüfen. |
| **Key Script** | `src/scripts/ingest_mth_profile_to_chroma.py` | MTH-Profil Tiefen-Chunking → ChromaDB mth_user_profile. |
| **Key Script** | `src/scripts/verify_vps_stack.py` | VPS: SSH, docker ps, Chroma v2 heartbeat; optionale Knoten Evolution, Monica, Kong (siehe VPS_KNOTEN_UND_FLUSSE). |
| **Benchmark** | `src/scripts/benchmark_whitepaper_anchors.py` | Paar-Benchmark **mit/ohne** Kardan (`omega_core`); JSONL unter `logs/benchmarks/`; Doku: `WHITE_PAPER_INFORMATIONSGRAVITATION_VOLLSTANDIG.md` § Empirie. |
| **Benchmark-Auswertung** | `src/scripts/evaluate_whitepaper_benchmark_log.py` | Prüft JSONL-Struktur und Plausibilität (Iterations-Paar, Outcomes). |
| **NotebookLM Whitepaper-Sanitize** | `Gemini_Json2md4NotebookLM/whitepaper_for_notebooklm.py` | 5d/WHITEPAPER → WHITEPAPER_NOTEBOOKLM: Zeilenumbruch, HTML-Kopfkommentare entfernt, Upload-freundliche Dateinamen. |
| **Science Council R2 (Ollama)** | `src/scripts/run_omega_science_council_r2.py` | Rat der Titanen: ausformuliertes Whitepaper → `5d/WHITEPAPER/reviews_2/` (lokal qwen2.5:14b). |
| **Science Council (Ollama)** | `src/scripts/run_omega_science_council.py` | Rat der Titanen: `--paper` / `--out`, Standard Kurzfassung → `OPERATION_OMEGA/REVIEWS/`. |
| **Science Council Profile** | `src/scripts/omega_science_council_profiles.py` | Titanen: `profil` + `kern_anker` (Formel/Prinzip); `num_ctx` Default 65536. |
| **Science Council Dossiers** | `docs/00_STAMMDOKUMENTE/SCIENCE_COUNCIL_DOSSIERS_FLAT/` | Flache Ordnerstruktur mit detaillierten Dossiers (Biografie, Werke, Interviews, Visuals) für alle 22 Titanen; Dateinamen = Namen der Personen. |
| **Science Council Gesamt** | `docs/00_STAMMDOKUMENTE/SCIENCE_COUNCIL_DOSSIERS_FLAT/SCIENCE_COUNCIL_DOSSIERS_GESAMT.md` | Konsolidierte Gesamt-Datei aller Titanen-Dossiers. |
| **MCP stdio** | `src/scripts/mcp_core_chroma_stdio.py` | Cursor/MCP: Tool `query_chromadb` (CORE_EICHUNG) → ChromaDB über `chroma_client`; Eintrag `core-chromadb` in `mcp_remote_config.json`. |
| **Database (PostgreSQL)** | `src/db/multi_view_client.py` | Multi-View Ingest & Search (pgvector & ChromaDB); kardanische Faltung. |
| **Database** | `src/db/core_infrastructure.sql` | 2D Integer-Membran (SQL-Schema) für CORE-Infrastruktur-Monitoring. |
| **Database** | `src/db/init_infrastructure.py` | Initialisierungs-Skript für die CORE-Infrastruktur-Tabelle auf VPS. |
| **Service** | `src/services/infrastructure_heartbeat.py` | Hintergrund-Service für periodisches Status-Monitoring (Dreadnought, Scout, VPS). |
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
| `.cursor/agents/` | Deterministische Sub-Agenten-Rollen (Layer 1). |
| `.cursor/rules/` | Kontextuelle Constraints via MDC-Globs (Layer 2). |
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
