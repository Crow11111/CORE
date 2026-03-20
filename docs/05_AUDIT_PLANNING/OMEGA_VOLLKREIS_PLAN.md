<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# OMEGA-Vollkreis-Plan: Geschlossene Kette, Team-Arbeitspakete, Linux-Auswirkungen

**Regel:** `@docs/BIBLIOTHEK_KERN_DOKUMENTE.md` immer einbinden.
**Ziel:** Gesamter Kreis nahtlos angebunden – Dreadnought ↔ Scout (HA) ↔ VPS ↔ MCP ↔ Git ↔ OC Brain ↔ Evolution/Monica/Kong/DBs. Geschlossene Kette ist **Must-Have**, kein Nice-to-Have; ohne sie Showstopper.

---

## 1. Was „Vollkreis“ bedeutet

- **Dreadnought** (Arch Linux): Backend :8000, Frontend :3000, Daemons, Ollama. **Zieht** von: VPS (Chroma, OC, Evolution, Monica, Postgres), Scout (HA), GitHub. **Drückt** nach: VPS (Chroma, Backup, OC, Evolution), Scout (HA-Services), GitHub (push).
- **Scout (Pi5):** HA :8123, Ollama, Tapo, WhatsApp-Addon (Fallback). **Zieht** von: CORE (Webhook-Antworten). **Drückt** nach: CORE (rest_command → /webhook/whatsapp, HA-Events).
- **VPS:** Chroma, OpenClaw, Evolution API, Monica, Kong, Postgres, AGI-Core, MCP, HA-Atlas. **Zieht** von: Dreadnought (API-Calls), GitHub (webhook → pull). **Drückt** nach: Dreadnought (Webhooks von Evolution/Git), CORE (Agent-Output von OC).
- **Git/GitHub:** **Zieht** von: Dreadnought (push). **Drückt** nach: VPS (webhook → pull), ggf. Dreadnought (Status/CI).
- **MCP / Claude Desktop / Ghost Agents:** Teil des Netzes; nutzen CORE/VPS nativ, regelbasiert Push/Pull.

Jeder Knoten muss **nativ** und **regelbasiert** (definierter Takt: was wann zieht, was wann drückt) angebunden sein. Das Ganze läuft auf Kernel-Ebene; der Takt muss nur gesetzt und gestartet werden.

---

## 2. Push/Pull-Definition (Kurzreferenz)

| Richtung | Inhalt | Takt / Trigger |
|----------|--------|-----------------|
| Dreadnought → VPS Chroma | Embedding-Upsert, Query | Bei Ingest, RAG, Gravitator |
| Dreadnought → VPS OC | Chat/RAG, Mirror-Events | Webhook-Verarbeitung, Trigger-Tasks |
| Dreadnought → Evolution API | WhatsApp sendText | Nach Triage/LLM (wenn Evolution konfiguriert) |
| Dreadnought → HA (Scout) | send_whatsapp, call_service | Command-Triage, Benachrichtigungen |
| Dreadnought → GitHub | push | Nach Takt 3 (Arbeiten); Takt 4 Ausstoß |
| VPS/Scout → Dreadnought | Webhooks (WhatsApp, HA, GitHub) | Eingehende Nachricht, Event, push-Event |
| VPS → Dreadnought | Chroma/Postgres/OC Antworten | API-Response auf Request |
| GitHub → VPS | pull (via Webhook) | Build-Engine, Kurbelwelle Takt 1 |

Vollständige Matrix: **`@docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md`**.

**Optional – prüfende Verifikation:** Deep Research (Gemini) kann vor oder nach der Abnahme eingesetzt werden, um Projekt Omega zu prüfen: Textverarbeitung, Vektorisierung, ChromaDB-Einlesen, Vektor-Abgleich. Checkliste und Auftragsformulierung: **`@docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md`**.

---

## 3. Team-Arbeitspakete (Bereiche)

Ein **Team** arbeitet die Bereiche ab; ein **Test-Team** prüft den Gesamtkreis; **Orchestrierung** (du) leitet und überwacht.

| Bereich | Verantwortung | Konkret |
|---------|--------------|---------|
| **A: Dreadnought (lokal)** | Backend, Frontend, Daemons, Ollama, Pfade, systemd | `.env`-Konsistenz, `run_verification.sh`, Ports 8000/3000, CORE_ROOT, Chroma-Lokal vs. VPS |
| **B: Scout / HA** | HA-API, rest_command, Automation, Tapo, WhatsApp-Addon (Fallback) | `HASS_URL`/`HASS_TOKEN` in .env; `rest_command.core_whatsapp_webhook`-URL = Dreadnought :8000 (vgl. CORE_HOST_IP, z. B. 192.168.178.20); E2E `run_whatsapp_e2e_ha`; Abnahme: HA API 200 |
| **C: VPS – Kern** | SSH, Docker, Chroma, OpenClaw Admin/Spine, MCP | `verify_vps_stack.py`, Chroma heartbeat, OC status, MCP erreichbar |
| **D: VPS – Erweiterte Dienste** | Evolution API, Monica, Kong, Postgres, atlas_agi_core | Evolution-Instanz + Webhook auf CORE; Monica/Kong/Postgres in Prozess einbinden; Verifikation pro Dienst |
| **E: Git/GitHub/Webhooks** | Remote, Push, Webhook-Empfang auf VPS, GIT_PULL_DIR | `git push`, Webhook-URL und Secret, `git pull` auf VPS nach push |
| **F: MCP / Claude Desktop / Ghost Agents** | MCP-Server, Cursor-Anbindung, Agenten-Kanäle | MCP „atlas-remote“ starten; Zugriff auf Workspace; regelbasierte Nutzung |
| **G: Integrationstest (Test-Team)** | E2E über alle Knoten | Jede Verbindung aus Testmatrix (OMEGA_LINUX_ORCHESTRATION) durchspielen; Showstopper-Check: geschlossene Kette |

**Bereich E – Webhook-Empfang auf dem VPS:** Der GitHub-Webhook wird von der CORE FastAPI-Route `POST /webhook/github` empfangen (Implementierung: `src/api/routes/github_webhook.py`). Damit der VPS nach Push `git pull` in `GIT_PULL_DIR` ausführt, muss der Webhook **auf dem VPS** ankommen: Entweder (a) die CORE-API (oder ein schlanker Dienst mit nur dieser Route) läuft auf dem VPS, mit `.env`-Variablen `GIT_PULL_DIR` und `GITHUB_WEBHOOK_SECRET`; in GitHub: Webhooks → Payload URL = `https://<VPS-Host>:<Port>/webhook/github` (z. B. Port 8000 oder hinter Kong/Reverse-Proxy). Oder (b) ein separater Listener auf dem VPS (z. B. eigenes kleines Skript mit HMAC-Prüfung und `git pull`) – dann ist die Einrichtung **manuell** vorzunehmen und nicht im Repo vorgegeben.


---

## 4. Auswirkungen des Linux-Umzugs (zu prüfen)

| Thema | Auswirkung | Prüfung / Maßnahme |
|-------|------------|---------------------|
| **Pfade** | Alle Windows-Pfade durch POSIX/CORE_ROOT ersetzt | `core_path_manager`, `.env`, Skripte ohne `C:\` |
| **systemd** | Backend/Frontend/Daemons autostart | `omega-backend`, `omega-frontend`, `omega-event-bus`, `omega-watchdog`, `omega-vision` |
| **Input-Injection** | ydotool/kdotool für Cursor; udev für uinput | `inject_cursor.sh`, Gruppe `input`, `/etc/udev/rules.d/80-uinput.rules` |
| **HA-Anbindung** | Scout-IP/Token unverändert; rest_command zeigt auf Dreadnought (neu: Arch-IP) | `HASS_URL`, `HASS_TOKEN`; rest_command URL = Dreadnought :8000 |
| **VPS-Zugriff** | SSH-Key unter Linux; gleiche Keys wie unter Windows nutzbar | `VPS_SSH_KEY`, `OPENCLAW_ADMIN_VPS_SSH_KEY`; `ssh -i ... root@$VPS_HOST` |
| **Chroma** | Lokal (Btrfs) oder nur VPS | `CHROMA_HOST`/`CHROMA_PORT` für VPS; ggf. lokale DB aus `core_path_manager` |
| **Git/pre-commit** | Python-Pfad und CRLF | `.venv/bin/python` in pre-commit; Zeilenenden LF |
| **Neue Möglichkeiten** | systemd, udev, native Skripte, Kernel-nah | Alle genutzt; Dokumentation in BIBLIOTHEK und Orchestrierung |

---

## 5. Abnahme / Testmatrix (messbar)

- **Dreadnought:** `curl -s http://localhost:8000/status` → event_bus.running true.
- **Scout:** `curl -sk -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/` → 200.
- **VPS:** `python -m src.scripts.verify_vps_stack` → Exit 0; optional: Evolution, Monica, Kong prüfen.
- **Chroma VPS:** `curl http://$VPS_HOST:32768/api/v2/heartbeat` → 200.
- **GitHub:** `git push origin main` → Exit 0.
- **WhatsApp E2E:** `python -m src.scripts.run_whatsapp_e2e_ha` → Antwort im Chat.
- **MCP:** Config: `mcp_remote_config.json` im Projekt-Root (valide, Eintrag `atlas-remote` mit SSH/Container). Cursor: MCP-Server „atlas-remote“ starten (Einstellungen → MCP / Referenz auf diese Datei); Abnahme: Zugriff auf Workspace prüfen (z. B. MCP-Tool list_dir/read_file auf /workspace).
- **Webhooks:** GitHub-Webhook an VPS konfiguriert; nach push: VPS führt pull in GIT_PULL_DIR aus.

Vollständige Testmatrix: **`@docs/02_ARCHITECTURE/OMEGA_LINUX_ORCHESTRATION.md`** (§4).

---

## 6. Abnahme-Protokoll (Orchestrator prüft selbst)

- **Regel:** Kein Vertrauen ohne eigenen Test. Die Teams A–F liefern; abgenommen wird erst, wenn der Orchestrator `run_vollkreis_abnahme.py` ausführt und alle Prüfungen bestehen.
- **Skript:** `run_vollkreis_abnahme.py` (Projekt-Root); Ausführung mit `.venv/bin/python run_vollkreis_abnahme.py`.
- **Letzte Abnahme:** Nach Team-Arbeit (Bereiche A–F) ausgeführt; Ergebnis: **PASS** (A–G grün). Geschlossene Kette messbar bestätigt.

## 7. Reihenfolge / Takt

1. **Dokumentation fest:** BIBLIOTHEK, VPS_KNOTEN_UND_FLUSSE, dieser Plan.
2. **Bereiche A–G** nacheinander oder parallel abarbeiten (Team); Verifikation pro Bereich.
3. **Integrationstest (G):** Gesamtkreis durchlaufen; alle Push/Pull-Pfade einmal ausführen.
4. **Commit & Push** von Dreadnought; Webhook-Prüfung auf VPS.
5. **Regelbetrieb:** Geschlossene Kette läuft; Takt (was wann zieht/drückt) in Cron/daemons/skripten verankert.

---

## 8. Referenzen

- Bereich A Prüfergebnis: **docs/05_AUDIT_PLANNING/Bereich_A_Dreadnought_Abnahme.md**
- BIBLIOTHEK_KERN_DOKUMENTE.md
- VPS_KNOTEN_UND_FLUSSE.md (Push/Pull-Detail)
- OMEGA_LINUX_ORCHESTRATION.md (Topologie, Testmatrix)
- CORE_SCHNITTSTELLEN_UND_KANAALE.md (5-Phasen-Motor, Kurbelwelle)
- WHATSAPP_E2E_HA_SETUP.md; Evolution als bevorzugter Pfad (VPS_KNOTEN_UND_FLUSSE)
