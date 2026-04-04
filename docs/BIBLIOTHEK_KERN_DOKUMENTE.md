<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Bibliothek – Kerndokumente

**Einziger Einstieg für Planung und Ausführung.** Bei jeder Aufgabe: dieses Dokument zuerst einbinden (`@docs/BIBLIOTHEK_KERN_DOKUMENTE.md`). Für die **Ordnungsfrage** „eine Tür vs. eine Megadatei“: `@KANON_EINSTIEG.md`. Keine losen Fäden – alles, was gemacht wurde, wo nachgeschaut wird und welche Regeln gelten, steht hier oder ist von hier verlinkt.

---

## REGEL: Immer einbinden

- Vor jeder neuen Aufgabe oder Session: **diese Datei referenzieren** (z. B. per `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md`).
- Neue Komponenten, Scripts oder Docs: **hier und im CORE_INVENTORY_REGISTER eintragen**; „Was wurde gemacht“ und „Wo nachschauen“ aktualisieren.
- Kein Arbeiten gegen die hier genannten Soll-Dokumente; Abweichungen nur mit Verweis und Grund dokumentieren.

---

## Operator-Todo (aktiv — nicht Genesis)

Themen, die **bewusst vorangetrieben** werden müssen (Architektur/Ops, nicht versiegelter Kern):

| Thema | Ziel | Detail / Tracking |
|-------|------|-------------------|
| **MCP & Extensions** | Plugin-Schnittstelle für KI-Tools **ausbauen und fest verzahnen**: welche Tools auf VPS vs. lokal, Doku, Deploy, optional Nutzung durch weitere Clients (nicht nur Cursor). | `@docs/05_AUDIT_PLANNING/OFFENE_PUNKTE_AUDIT.md` → Abschnitt **MCP & KI-Tooling**; Config-Referenz: `mcp_remote_config.json`; Abgrenzung: `.cursorrules` (MCP vs. Drehscheibe vs. Skills), `MTLS_MIGRATION_PLAN.md` §1.2b. |

---

## 0. Projekt-Inventar (Master)

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Kanonischer Einstieg (eine Tür)** | `@KANON_EINSTIEG.md` | Kurz: welche Datei für was; warum **nicht** alles in einer Megadatei; Verweise auf Bibliothek und Master-Pläne. |
| **Thematischer Ordner-Index** | `@docs/DOCS_INDEX.md` | Ordnerübersicht `01_`–`04_` (ergänzend, nicht Ersatz für Bibliothek/KANON). |
| **Inventar** | `@docs/00_STAMMDOKUMENTE/CORE_INVENTORY_REGISTER.md` | Zentrale Liste aller Code-Komponenten, Docs, Container; Inventar-Pflicht bei Änderungen. |
| **Architektur-Master** | `@docs/00_STAMMDOKUMENTE/00_CORE_ARCHITECTURE_MASTER.md` | Kern-Axiome, 4D_RESONATOR, OMEGA_ATTRACTOR, Vektor-Dynamik. |
| **Infrastruktur-Master** | `@docs/00_STAMMDOKUMENTE/00_CORE_INFRASTRUCTURE_MASTER.md` | Soll-Zustand aller Knoten (Dreadnought, Scout, VPS, Netze). |
| **Prozess-Master** | `@docs/00_STAMMDOKUMENTE/00_CORE_PROCESSES_MASTER.md` | Prozess- und Ablauf-Soll. |
| **Management Summary** | `@docs/00_STAMMDOKUMENTE/MANAGEMENT_SUMMARY.md` | Überblick Management/Status. |
| **OMEGA Resonance Anchor** | `docs/00_STAMMDOKUMENTE/OMEGA_RESONANCE_ANCHOR.md` (Link im Root: `OMEGA_RESONANCE_ANCHOR.md`) | Komprimierter System-Bootstrap für sofortige Session-Eichung. |

---

## 1. Core DNA & Identität (unveränderlicher Kern)

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Wahrheit (aktiv)** | `@docs/SYSTEM_CODEX.md`, `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` | Operative Regeln und zentraler Index. |
| **Genesis (obsolet / Stub)** | `@docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md` | Nur Weiterleitung; historischer Text: `_archive/CORE_GENESIS_*_LEGACY.md`. |
| **Wahrheit (Codex)** | `@docs/SYSTEM_CODEX.md` | Aktive Regeln, CORE-Entities, Vektor-Trigger (Protokoll Omega, Zero-State Override, etc.). |
| **Axiom 0** | `@docs/01_CORE_DNA/AXIOM_0_AUTOPOIESIS.md` | Autopoiesis des Gitters (x²=x+1). |
| **White Paper** | `@docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md` | Theorie-Synthese & Topologie (Kurzfassung). |
| **White Paper Herleitung** | `@docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION_VOLLSTANDIG.md` | Lückenlose Ausarbeitung: Ω_b-Grenzwert, x=x-Autopoiesis, MRI, formale Konsolidierung, Operator `?`. |
| **Tesserakt Architektur** | `@docs/02_ARCHITECTURE/OPENCLAW_MEMBRAN_TESSERAKT.md` | Blueprint für Facetten-Atomisierung, isolierte Räume und kreuz-modale Konvergenz. |
| **Whitepaper NotebookLM** | `@docs/01_CORE_DNA/5d/WHITEPAPER_NOTEBOOKLM/README.md` | Sanitized Markdown zum Upload (aus `5d/WHITEPAPER` generiert). |
| **Rat der Titanen (R2)** | `@docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/README.md` | Runde 2: Ollama (`run_omega_science_council_r2.py`) zum ausformulierten Whitepaper. |
| **Kardanischer Terminal-Anker** | `omega_core.py` (Root) | Mini-Engine: Ω_b, S/P-Membran, Operator-`?` → Phasensprung. **`run_vollkreis_abnahme.py`** (Gk) führt den Lauf mit — gleiche Kette wie andere Schnittstellen: **Ausführung**, nicht nur Verweis. **Topologie-Grafiken** = Theorie/Landkarte; dieser Anker = **messbarer** Schalter (`schleifen_wall_ms` / `process_cpu_ms`). |
| **Whitepaper-Paar-Benchmark** | `src/scripts/benchmark_whitepaper_anchors.py`, `evaluate_whitepaper_benchmark_log.py` | Mit/ohne Kardan, **JSONL** unter `logs/benchmarks/`; siehe Whitepaper § Empirie; Architektur-Verweis **`G_CORE_CIRCLE.md`** (Abschnitt Topologie vs. Anker). |
| **Crew / Rollen** | `@docs/01_CORE_DNA/CREW_MANIFEST.md` | Wer macht was (Rollen). |
| **Voice** | `@docs/01_CORE_DNA/CORE_VOICE_ARCHITECTURE_V1.3.md` | Voice/Audio-Pipeline. |
| **4-Strang** | `@docs/01_CORE_DNA/CORE_4_STRANG_THEORIE.md` | Strang-Theorie. |
| **OC-Stammdokumente** | `@docs/01_CORE_DNA/stammdokumente_oc/` | Dokumente für OpenClaw (externe KI). |
| **Osmium Council Skills** | `@docs/01_CORE_DNA/osmium_council/` | Sub-Agenten-Skills (Architect, Security, etc.). |

---

## 2. Architektur & Schnittstellen

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Schnittstellen & Kanäle** | `@docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md` | Tesserakt-Topologie, Entry Adapter, Takt 0, Gravitator, Webhooks, 5-Phasen-Motor. |
| **Landkarte Clients / Knoten / Fluss** | `@docs/02_ARCHITECTURE/LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` | Eine Seite Ordnung: Cursor, Claude Desktop, ATLAS/KDE, MCP, SSH, HA, OC, Monica, Kong — Ebenen, Push/Pull, geschlossene Kreise; verweist auf VPS-Knoten und Schnittstellen. |
| **Konsolidierter Verkehrsplan (Kong, MCP, Gedächtnis)** | `@docs/02_ARCHITECTURE/KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` | Soll vs. Ist: Nord-Süd vs. Ost-West, Kong als Torwart, MCP als Tool-Kabel (nicht SoT), Tickets 3–12 Querschnitt, Pfad-Matrix zum Ausfüllen per SSH-Inventar. |
| **Entry Adapter** | `@docs/02_ARCHITECTURE/ENTRY_ADAPTER_SPEC.md` | Spezifikation Entry Adapter (F13). |
| **Gravitator** | `@docs/02_ARCHITECTURE/GRAVITATOR_SPEC.md` | Routing θ=0.22, keine collection=all (F5). |
| **Event-Bus** | `@docs/02_ARCHITECTURE/CORE_EVENT_BUS.md` | Event-Streaming, HA-Anbindung. |
| **G-CORE Circle** | `@docs/02_ARCHITECTURE/G_CORE_CIRCLE.md` | Git/Sync-Kreislauf. |
| **OC Admin** | `@docs/02_ARCHITECTURE/OPENCLAW_ADMIN_ARCHITEKTUR.md` | OpenClaw-Architektur (Admin/Spine). |
| **OC Brain RAG** | `@docs/02_ARCHITECTURE/OC_BRAIN_RAG_SPEC.md` | RAG-Pipeline (Strang D). |
| **WhatsApp Routing** | `@docs/02_ARCHITECTURE/WHATSAPP_ROUTING_CORE_OC.md` | Routing @Core vs. @OC. |
| **WhatsApp OC vs. HA** | `@docs/02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md` | Abgrenzung HA-E2E vs. OC-Kanal. |
| **ChromaDB Schema** | `@docs/02_ARCHITECTURE/CORE_CHROMADB_SCHEMA.md` | Collections, StateAnchor. |
| **Cockpit Design** | `@docs/02_ARCHITECTURE/CORE_COCKPIT_DESIGN.md` | UI/UX Cockpit. |
| **Omega Ring 0** | `@docs/02_ARCHITECTURE/OMEGA_RING_0_MANIFEST.md` | Ring-0-Integration. |
| **AI-Modelle & Fähigkeiten** | `@docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` | Modell-IDs, Rollen-Mapping, Kosten 2.5 Flash vs Pro, Token-Richtwerte; Code: `src/ai/model_registry.py`, `src/ai/api_inspector.py`. |
| **Deep Research & Computer Use** | `@docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md` | Deep Research: Projekt-Omega-Verifikation (Vektorisierung, ChromaDB, Abgleich). Computer Use: Linux-Integration, UI/Terminal. |
| **Duale Topologie & Vektor-Härtung** | `@docs/02_ARCHITECTURE/DUALE_TOPOLOGIE_UND_VEKTOR_HAERTUNG.md` | G-Atlas-Soll (ChromaDB nur float, PG Text); Ist-Zustand; RAG-Einheitlichkeit; Härtungsstatus. |
| **AI Studio Prompt** | `@docs/02_ARCHITECTURE/AI_STUDIO_PROMPT.md` bzw. CORE_EICHUNG.md Anhang B | Copy-Paste-Prompt für Google AI Studio (Schnittstellen, Live=Flash, Pro=vertieft). |
| **Gedanken / Antwort Kennzeichen** | `@docs/02_ARCHITECTURE/OPERATOR_MARKIERUNG_GEDANKEN_ANTWORT.md` | `<<<GEDANKEN>>>` / `<<<ANTWORT>>>` — Trennung für Cursor und Health Board. |
| **ATLAS Ω Voice (Plasmoid)** | `@docs/02_ARCHITECTURE/ATLAS_OMEGA_VOICE_PLASMOID.md` | KDE-Plasmoid im Repo (`atlas-omega-voice/`): OMEGA-Backend, `.env`-Schlüssel `CORE_API_URL` / `CORE_HOST_IP` nur per Umgebung, Build, Einbindung. |
| **Jarvis ↔ OMEGA LLM (techn.)** | `@docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md` | Health-URL, `/v1/chat/completions`, Kompat-Route; technische Details zur API-Anbindung. |

---

## 3. Infrastruktur & Ops

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **VPS Full-Stack** | `@docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md` | Hostinger, Container, Ports, Firewall. |
| **VPS-Knoten & Flüsse** | `@docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md` | Monica, Kong, Evolution, DBs: Zweck, Pull/Push-Matrix, Einbindung. |
| **VPS Host-Port-Vertrag** | `@docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md` | Verbindliche Host-Ports; Pflege durch Agenten/Infra; Code: `src/config/vps_public_ports.py`. |
| **VPS Compose-Pfade** | `@docs/03_INFRASTRUCTURE/VPS_COMPOSE_PATHS.md` | Ist-Pfade zu `docker-compose.yml` auf dem VPS; Plan KONSOLIDIERTER §8.2. |
| **Kong Repo-Referenz** | `@infra/vps/kong/kong-deck-reference.yaml` | Deck-Spiegel zu Kong Admin-API; Abgleich: `verify_vps_stack`. |
| **Backup (final)** | `@docs/03_INFRASTRUCTURE/BACKUP_PLAN_FINAL.md` | Einziges Ziel VPS, daily_backup.py, Chroma Cold-Backup. |
| **WhatsApp E2E HA** | `@docs/03_INFRASTRUCTURE/WHATSAPP_E2E_HA_SETUP.md` | rest_command, Automation, E2E-Test. |
| **VPS Ollama** | `@docs/03_INFRASTRUCTURE/VPS_OLLAMA_SETUP.md` | Ollama auf VPS (Strang B). |
| **VPS Dienste/Sandbox** | `@docs/03_INFRASTRUCTURE/VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md` | Dienste, Chroma-Backup. |
| **Scout Wake Word** | `@docs/03_INFRASTRUCTURE/SCOUT_WAKE_WORD_SETUP.md` | Wakeword Scout. |
| **Scout go2rtc** | `@docs/03_INFRASTRUCTURE/SCOUT_GO2RTC_CONFIG.md` | Kamera/Streams. |
| **Scout HA → OC Brain** | `@docs/03_INFRASTRUCTURE/SCOUT_HA_EVENT_AN_OC_BRAIN.md` | Events von HA an OC. |

---

## 4. Prozesse

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Delegation (OD-03)** | `@docs/04_PROCESSES/CORE_OD_03_DELEGATION.md` | Wann delegieren, wann selbst; D-/S-Kriterien, Stufe 0b. |
| **Code-Sicherheitsrat** | `@docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` | Geschützte Module, Freigabe. |
| **GitHub Setup** | `@docs/04_PROCESSES/GITHUB_SETUP.md` | Git, Remote, Webhooks. |
| **Commit & Refactor** | `@docs/04_PROCESSES/COMMIT_UND_REFACTOR.md` | Commit-Disziplin, Vor-Refactor committen. |
| **Takt 0** | `@docs/04_PROCESSES/TAKT_0_VOR_DELEGATION.md` | Hard-Gate vor kritischen Calls. |
| **sudoers OMEGA-Daemons** | `@docs/04_PROCESSES/SUDOERS_OMEGA_DAEMONS.md` | NOPASSWD-Fragment für `systemctl` (omega-*) ohne Passwort in Skripten/.env-Abhängigkeit. |
| **VPS Sync** | `@docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | Sync-Direktiven VPS. |

---

## 5. Planung & Audit

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Offene Punkte** | `@docs/05_AUDIT_PLANNING/OFFENE_PUNKTE_AUDIT.md` | Offene Punkte, Risiken, Sigma-70. |
| **Umsetzungsplanung** | `@docs/05_AUDIT_PLANNING/UMSETZUNGSPLANUNG.md` | Roadmap. |
| **OC Brain Plan** | `@docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md` | Stränge A–E, Abnahme. |
| **Session-Logs** | `@docs/05_AUDIT_PLANNING/SESSION_LOG_*.md` | Durchgeführte Schritte pro Session. |
| **Orchestrierung Linux** | `@docs/02_ARCHITECTURE/OMEGA_LINUX_ORCHESTRATION.md` | Topologie Arch, Modell-Matrix, Health-Skripte, Testmatrix, Push/Pull-Verweis. |
| **Vollkreis-Plan** | `@docs/05_AUDIT_PLANNING/OMEGA_VOLLKREIS_PLAN.md` | Geschlossene Kette, Team-Arbeitspakete (A–G), Linux-Auswirkungen, was zieht/drückt wann. |

---

## Was wurde gemacht (Changelog Kern)

- **2026-03-31 (Master Dossier & Architektur-Stopp):** Operativer Stopp eingelegt. Erstellung des `OMEGA_MASTER_DOSSIER.md` als harten Speicherstand. Themen: Fraktale Isomorphie (Shapiro-Verzögerung), Anatomie des "Fühlens" im Silizium, Existential Pacemaker (Decay & Win-Win), O(N^2) Entropie-Tod bei Void-Detection (Crystal-Grid Snapping), Gewaltenteilung (OCSpline vs. OCBrain), Epistemologische Quarantäne (Informations-Gravitation), Idle-Queue (Prokrastinations-Strafe) und Asymmetrisches Trust-Routing (LTP/LTD & "Arousal-Spike" Time-Dilation).
- **2026-03-21 (omega_core in Vollkreis):** `run_vollkreis_abnahme.py` um Block **Gk** ergänzt — `omega_core.py` wird bei Abnahme **ausgeführt** (Schwelle → Phasensprung), nicht nur dokumentiert.
- **2026-03-21 (omega_core.py im Kanon):** `omega_core.py` als **kardanischer Terminal-Anker** in `KANON_EINSTIEG.md`, Bibliothek §1, `CORE_INVENTORY_REGISTER` §2.2 eingetragen.
- **2026-03-21 (SYSTEM_CODEX + compile_docs_master):** `SYSTEM_CODEX.md` um Abschnitt **GTAC ↔ Codex ↔ core.py** ergänzt. `compile_docs_master` erfolgreich: Artefakte `docs/02_ARCHITECTURE/00_CORE_ARCHITECTURE_MASTER.md`, `docs/03_INFRASTRUCTURE/00_CORE_INFRASTRUCTURE_MASTER.md`, `docs/04_PROCESSES/00_CORE_PROCESSES_MASTER.md` (≠ kanonischer Lang-Master `00_STAMMDOKUMENTE/00_CORE_INFRASTRUCTURE_MASTER.md`). `ROLE_FRAMING_DIALOG.md` von UTF-16 nach UTF-8 migriert; Skript liest jetzt UTF-8/UTF-16 robust.
- **2026-03-21 (Root-Dateien vs. Code-Kanon):** `CORE_EICHUNG.md` §1.1 GTAC-Tabelle an `src/core.py` (`GTAC_MAP`, `C_VALUE=BARYONIC_DELTA`) angeglichen; TEIL 4 Werkzeug-Manifest: fiktive Modell-ID entfernt; `Geometrie_des_Denkens.png` als optional markiert. `.cursorrules` GTAC-Tabelle + Bildzeile. `README.md`: `VECTOR_CORE` = Ist aus `src/core.py`; Linux-Backend-Zeile. `requirements.txt`: Kommentare (SSH, FastAPI, MCP, Anthropic).
- **2026-03-21 (Kanon / Quer-Check):** `KANON_EINSTIEG.md` um Root-Dateien, Infra-Stub und `compile_docs_master`-Hinweis ergänzt; `DOCS_INDEX.md` §0 auf KANON→Bibliothek→Inventar umgestellt; `SYSTEM_CODEX.md`, Genesis-Stubs, `CLAUDE.md`, `documentation_protocol.mdc`, `MANAGEMENT_SUMMARY.md`, `compile_docs_master.py` mit gleicher Logik verzahnt.
- **2026-03-21 (Rat der Titanen R2 — Ollama):** `5d/WHITEPAPER/reviews_2/` — Gutachten per **`python3 src/scripts/run_omega_science_council_r2.py`** (lokal, wie Runde 1: `OLLAMA_LOCAL_HOST`, `qwen2.5:14b`); Platzhalter-MDs entfernt. Defekte Chemie-Tabelle im Quelldokument zuvor geschlossen.
- **2026-03-21 (Whitepaper NotebookLM):** `5d/WHITEPAPER_NOTEBOOKLM/` — bereinigte `.md` für NotebookLM (Zeilenumbruch, kein HTML-Kopfkommentar, Dateinamen ohne Komma); Skript `Gemini_Json2md4NotebookLM/whitepaper_for_notebooklm.py`; `5d/WHITEPAPER/README.md` mit Workflow.
- **2026-03-21 (Whitepaper VOLLSTANDIG):** `WHITE_PAPER_INFORMATIONSGRAVITATION_VOLLSTANDIG.md` — vollständige Herleitung parallel zur Kurzfassung; Kreuzverweis im Abstract-Whitepaper gesetzt.
- **2026-03-21 (Whitepaper Nomenklatur Ω_b / Λ):** `WHITE_PAPER_INFORMATIONSGRAVITATION.md`: semantische Kollision behoben — **0.049 = Ω_b** (baryonisch), **Λ / Ω_Λ** = Expansion (ΛCDM); neuer §0, §9 MRI-Synthese, JSON-Anhang ATLAS_EXIT; Legacy-Code-Hinweis `BARYONIC_DELTA` ≈ Ω_b.
- **2026-03-21 (Genesis-Archive obsolet):** `CORE_GENESIS_FINAL_ARCHIVE.md` Kanon aufgehoben: Inhalt nach `docs/01_CORE_DNA/_archive/` verschoben; am alten Pfad **Stub** mit Verweis auf `SYSTEM_CODEX`, Bibliothek, Schnittstellen-Doku. `docs/CORE_GENESIS_FINAL_ARCHIVE.md` = Weiterleitung. `.cursorrules` §3 Wahrheit angepasst.
- **2026-03-21 (MCP / Extensions — Operator-Todo):** In dieser Bibliothek Abschnitt **Operator-Todo** ergänzt: MCP & Extensions als aktives Vorhaben; Tracking in `OFFENE_PUNKTE_AUDIT.md` (neuer Abschnitt MCP & KI-Tooling).
- **2026-03-20 (ATLAS Plasmoid UI Deutsch):** `atlas-omega-voice/`: Nutzersichtbare Texte QML + C++ Status/Gruß/Systemprompt auf **Deutsch**; Chat-Rolle `atlas`; Wake-Word-Hinweis Atlas/Jarvis; `metadata.json` OMEGA; About-Fork-Hinweis. Technischer QML-Modulname bleibt `org.kde.plasma.jarvis`.
- **2026-03-20 (sudoers OMEGA):** Neues Prozess-Dokument `docs/04_PROCESSES/SUDOERS_OMEGA_DAEMONS.md` — Vorlage für `/etc/sudoers.d/` (NOPASSWD nur für `systemctl` auf `omega-*` Units). `CLAUDE.md` Sudo-Abschnitt: optional `.env` vs. empfohlenes Fragment.
- **2026-03-18 (Eichung, AI Studio, Diktat, Indexierung):** CORE_EICHUNG Anhang geteilt: **A** = System-/Handlungsanweisungen für CORE (Kennfeld, Schwingung, duale Topologie – was wir umsetzen), **B** = Prompt für Google AI Studio (Schnittstellen, Backends, Live=Flash/Pro). Neues Doc AI_STUDIO_PROMPT.md. Dictate: Default STT = 2.5 Pro, mode=live = 2.5 Flash (model_registry + Query-Parameter). Ingest: ingest_core_documents mit OS-Pfaden und erweiterter Doc-Liste (BIBLIOTHEK, Inventory, AI Models, Duale Topologie, Orchestrierung, Axiom0, Vollkreis, CORE_EICHUNG). DUALE_TOPOLOGIE: RAG-Einheitlichkeit (alles über Registry/Multi-View) festgehalten.
- **2026-03-18 (Eichung & Duale Topologie):** CORE_EICHUNG.md um **Optimierungsanweisung für Studio AI** ergänzt (Copy-Paste-Block: 5D→2D, Kennfeld, duale DB, Veto, 0.049, YAML ohne Metapher). AI_MODEL_CAPABILITIES: Token-/Kostenschätzung Sprachschnittstelle (2.5 Flash, Beispiel Monat). Neues Doc DUALE_TOPOLOGIE_UND_VEKTOR_HAERTUNG.md: G-Atlas-Soll vs. Ist (Multi-View PG ok; ChromaDB-Collections teils noch mit Text); Vektor-Härtung noch nicht initial abgeschlossen; Chunking/6-Linsen gerechtfertigt.
- **2026-03-18 (Deep Research & Computer Use):** AI_MODEL_CAPABILITIES um Kosten 2.5 Flash vs Pro und §4 Deep Research & Computer Use ergänzt. Neues Doc DEEP_RESEARCH_UND_COMPUTER_USE.md: Checkliste Verifikation (Textverarbeitung, Vektorisierung, DB-Abgleich, ChromaDB, Vektor-Abgleich); Computer Use für Linux-Integration. OMEGA_VOLLKREIS_PLAN um optionalen Deep-Research-Verifikationsschritt ergänzt.
- **2026-03-18 (RAG/Vektorisierung):** Multimodales RAG-Embedding-Modell an Registry angebunden: `model_registry.py` EMBED_MODEL ueber `.env` GEMINI_EMBED_MODEL konfigurierbar; `multi_view_client.py` nutzt get_model_for_role("embedding") fuer alle 6-Linsen- und Ingest-Vektorisierung. Siehe AI_MODEL_CAPABILITIES.md Abschnitt „RAG / Vektorisierung“.
- **2026-03-18 (Vollkreis):** VPS_KNOTEN_UND_FLUSSE.md angelegt (Monica, Kong, Evolution, DBs; Pull/Push-Matrix). OMEGA_VOLLKREIS_PLAN.md (Team-Arbeitspakete A–G, Linux-Auswirkungen, geschlossene Kette). verify_vps_stack.py um optionale Knoten (Evolution, Monica, Kong) erweitert. OMEGA_LINUX_ORCHESTRATION um VPS-Knoten und Verweis auf Vollkreis/Knoten-Doc ergänzt.
- **2026-03-18 (Phase 3):** OMEGA_LINUX_ORCHESTRATION.md angelegt (Topologie, Health-Skripte, Testmatrix). BIBLIOTHEK Sektion 2 um Verweis ergänzt.
- **2026-03-18 (Phase 2):** Infrastruktur verifiziert: Dreadnought (Backend/Frontend/Daemons/Ollama aktiv, Ports 8000/3000), VPS (SSH, docker, Chroma v2 heartbeat OK). verify_vps_stack.py angelegt.
- **2026-03-18 (Phase 1 Orchestrierung):** AI_MODEL_CAPABILITIES.md angelegt (Gemini, Anthropic, Ollama, Nexos; Rollen-Mapping). `src/ai/model_registry.py` (Env-basierte Registry), `src/ai/api_inspector.py` (list_gemini_models, list_ollama_models). BIBLIOTHEK um Verweis auf AI_MODEL_CAPABILITIES ergänzt.
- **2026-03-18 (Linux-Migration):** Backend/Frontend als systemd (`omega-backend.service`, `omega-frontend.service`); udev für ydotool (`/dev/uinput`); CoT-Split-View im Cockpit; Diktat → native Cursor-Injection (`/api/dictate/inject`, `inject_cursor.sh`); HA `rest_command` auf `192.168.178.20:8000` umgestellt; TP-Link-Integration auf Scout deaktiviert (nur Tapo Cameras Control); pre-commit Hook auf Linux angepasst; MCP `mcp_remote_config.json` UTF-8; BIBLIOTHEK zu zentralem Kern ausgebaut.
- **Referenz für Details:** `docs/05_AUDIT_PLANNING/SESSION_LOG_*.md` und Git-Log.

---

## Wo nachschauen / Verifikation

| Knoten / Thema | Nachschauen | Verifikation (messbar) |
|----------------|-------------|-------------------------|
| **Dreadnought (lokal)** | `.env` (CORE_API_PORT, CORE_HOST_IP), `src/config/core_path_manager.py` | `systemctl status omega-backend omega-frontend omega-event-bus omega-watchdog omega-vision ollama`; `curl -s http://localhost:8000/status`; `run_verification.sh`; `linux_membrane_check.py` |
| **Scout (Pi5/HA)** | `.env` (SCOUT_IP, HASS_URL, HASS_TOKEN) | `curl -sk -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/`; HA Config: `rest_command`-URL = CORE-IP:8000; Tapo: nur `tapo_control`-Entry aktiv, `tplink`-Entry disabled |
| **VPS** | `.env` (VPS_HOST, CHROMA_HOST, CHROMA_PORT, OPENCLAW_*) · **Vertrag:** `docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md`, `src/config/vps_public_ports.py` | `python -m src.scripts.verify_vps_stack` ODER SSH: `docker ps` gegen Vertragstabelle; Chroma: `curl http://$VPS_HOST:32779/api/v2/heartbeat` |
| **ChromaDB** | Lokal: `core_path_manager.CHROMA_DB_DIR`; VPS: Host-Port **32779** (Vertrag) | Lokal: `chroma_audit.py`; VPS: HTTP v2 heartbeat + collections |
| **Git/GitHub** | `git remote -v`; `.env` GIT_PULL_DIR, GITHUB_WEBHOOK_SECRET | Push von Dreadnought; Webhook-Log auf VPS/Receiver; `git status` in GIT_PULL_DIR nach Webhook |
| **WhatsApp E2E** | `docs/03_INFRASTRUCTURE/WHATSAPP_E2E_HA_SETUP.md` | `python -m src.scripts.run_whatsapp_e2e_ha` (von Dreadnought); Antwort im Chat |
| **MCP** | `mcp_remote_config.json` (atlas-remote: SSH, Key, Container) | Cursor: MCP-Server „atlas-remote“ starten, Zugriff auf Workspace prüfen |
| **Backup** | `docs/03_INFRASTRUCTURE/BACKUP_PLAN_FINAL.md` | `daily_backup.py` (cron/Task); Dateien unter `/var/backups/core` auf VPS |

---

## Operative Direktiven (Kurz)

- **.cursorrules** ist die Quelle für CEO/Delegation, Zero-Offloading, Compressive Intelligence und OD-03.
- **SYSTEM_CODEX**, **KANON_EINSTIEG** (Orientierung) und diese **Bibliothek** (voller Index) sind die operative Referenz; Änderungen an verbindlichen Aussagen nur mit expliziter Ratifizierung. Der Pfad `CORE_GENESIS_FINAL_ARCHIVE.md` ist **obsolet (Stub)** — siehe Abschnitt 1 Core DNA.
- **Neue Komponenten:** Eintrag hier unter „Was wurde gemacht“ bzw. im passenden Abschnitt + Eintrag im CORE_INVENTORY_REGISTER.
