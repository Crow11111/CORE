<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Bibliothek – Kerndokumente

**Einziger Einstieg für Planung und Ausführung.** Bei jeder Aufgabe: dieses Dokument zuerst einbinden (`@docs/BIBLIOTHEK_KERN_DOKUMENTE.md`). Keine losen Fäden – alles, was gemacht wurde, wo nachgeschaut wird und welche Regeln gelten, steht hier oder ist von hier verlinkt.

---

## REGEL: Immer einbinden

- Vor jeder neuen Aufgabe oder Session: **diese Datei referenzieren** (z. B. per `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md`).
- Neue Komponenten, Scripts oder Docs: **hier und im CORE_INVENTORY_REGISTER eintragen**; „Was wurde gemacht“ und „Wo nachschauen“ aktualisieren.
- Kein Arbeiten gegen die hier genannten Soll-Dokumente; Abweichungen nur mit Verweis und Grund dokumentieren.

---

## 0. Projekt-Inventar (Master)

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Inventar** | `@docs/00_STAMMDOKUMENTE/CORE_INVENTORY_REGISTER.md` | Zentrale Liste aller Code-Komponenten, Docs, Container; Inventar-Pflicht bei Änderungen. |
| **Architektur-Master** | `@docs/00_STAMMDOKUMENTE/00_CORE_ARCHITECTURE_MASTER.md` | Kern-Axiome, 4D_RESONATOR, OMEGA_ATTRACTOR, Vektor-Dynamik. |
| **Infrastruktur-Master** | `@docs/00_STAMMDOKUMENTE/00_CORE_INFRASTRUCTURE_MASTER.md` | Soll-Zustand aller Knoten (Dreadnought, Scout, VPS, Netze). |
| **Prozess-Master** | `@docs/00_STAMMDOKUMENTE/00_CORE_PROCESSES_MASTER.md` | Prozess- und Ablauf-Soll. |
| **Management Summary** | `@docs/00_STAMMDOKUMENTE/MANAGEMENT_SUMMARY.md` | Überblick Management/Status. |

---

## 1. Core DNA & Identität (unveränderlicher Kern)

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Wahrheit (Genesis)** | `@docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md` | Versiegeltes Fundament; 4D_RESONATOR vs. OMEGA_ATTRACTOR, MTH-Matrix. |
| **Wahrheit (Codex)** | `@docs/SYSTEM_CODEX.md` | Aktive Regeln, CORE-Entities, Vektor-Trigger (Protokoll Omega, Zero-State Override, etc.). |
| **Axiom 0** | `@docs/01_CORE_DNA/AXIOM_0_AUTOPOIESIS.md` | Autopoiesis des Gitters (x²=x+1). |
| **White Paper** | `@docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md` | Theorie-Synthese & Topologie. |
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
| **VPS** | `.env` (VPS_HOST, CHROMA_HOST, CHROMA_PORT, OPENCLAW_*) | `python -m src.scripts.verify_vps_stack` ODER SSH: `ssh -i $VPS_SSH_KEY root@$VPS_HOST "docker ps"`; Chroma: `curl http://$VPS_HOST:32768/api/v2/heartbeat`; OC Admin/Spine: Container „Up“, Logs prüfen |
| **ChromaDB** | Lokal: `core_path_manager.CHROMA_DB_DIR`; VPS: Port 32768 | Lokal: `chroma_audit.py`; VPS: HTTP v2 heartbeat + collections |
| **Git/GitHub** | `git remote -v`; `.env` GIT_PULL_DIR, GITHUB_WEBHOOK_SECRET | Push von Dreadnought; Webhook-Log auf VPS/Receiver; `git status` in GIT_PULL_DIR nach Webhook |
| **WhatsApp E2E** | `docs/03_INFRASTRUCTURE/WHATSAPP_E2E_HA_SETUP.md` | `python -m src.scripts.run_whatsapp_e2e_ha` (von Dreadnought); Antwort im Chat |
| **MCP** | `mcp_remote_config.json` (atlas-remote: SSH, Key, Container) | Cursor: MCP-Server „atlas-remote“ starten, Zugriff auf Workspace prüfen |
| **Backup** | `docs/03_INFRASTRUCTURE/BACKUP_PLAN_FINAL.md` | `daily_backup.py` (cron/Task); Dateien unter `/var/backups/core` auf VPS |

---

## Operative Direktiven (Kurz)

- **.cursorrules** ist die Quelle für CEO/Delegation, Zero-Offloading, Compressive Intelligence und OD-03.
- **Genesis (CORE_GENESIS_FINAL_ARCHIVE, SYSTEM_CODEX)** hat Vorrang; Änderungen an „Wahrheit“ nur mit expliziter Ratifizierung.
- **Neue Komponenten:** Eintrag hier unter „Was wurde gemacht“ bzw. im passenden Abschnitt + Eintrag im CORE_INVENTORY_REGISTER.
