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
| **AI-Modelle & Fähigkeiten** | `@docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` | Modell-IDs, Rollen-Mapping, Token-Richtwerte; Code: `src/ai/model_registry.py`, `src/ai/api_inspector.py`. |

---

## 3. Infrastruktur & Ops

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **VPS Full-Stack** | `@docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md` | Hostinger, Container, Ports, Firewall. |
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
| **VPS Sync** | `@docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | Sync-Direktiven VPS. |

---

## 5. Planung & Audit

| Dokument | Pfad | Funktion |
|----------|------|----------|
| **Offene Punkte** | `@docs/05_AUDIT_PLANNING/OFFENE_PUNKTE_AUDIT.md` | Offene Punkte, Risiken, Sigma-70. |
| **Umsetzungsplanung** | `@docs/05_AUDIT_PLANNING/UMSETZUNGSPLANUNG.md` | Roadmap. |
| **OC Brain Plan** | `@docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md` | Stränge A–E, Abnahme. |
| **Session-Logs** | `@docs/05_AUDIT_PLANNING/SESSION_LOG_*.md` | Durchgeführte Schritte pro Session. |
| **Orchestrierung Linux** | `@docs/02_ARCHITECTURE/OMEGA_LINUX_ORCHESTRATION.md` | Topologie Arch, Modell-Matrix, Health-Skripte, Testmatrix. Detailplan: Cursor Plan „omega-linux-reorchestrierung“. |

---

## Was wurde gemacht (Changelog Kern)

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
