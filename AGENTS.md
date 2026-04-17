# AGENTS.md — OMEGA_CORE

Einstieg für **Cloud- und KI-Agenten** (Cursor, Remote). Ergänzt **`.cursorrules`** und **`CLAUDE.md`**; ersetzt sie nicht.

---

## Cursor User Rules (Spiegel)

Diesen Abschnitt kannst du **1:1** unter **Cursor → Settings → Rules → User Rules** einfügen (damit er **global** gilt, nicht nur aus dem Repo):

**Deutsch:** Zu jeder **größeren** Aufgabe (Architektur, VPS/Kong, Multi-Modul) zuerst MCP **`get_orchestrator_bootstrap`** (Server **`user-omega-state-mcp`**) mit kurzem **`task_hint`** aufrufen; **`gaps`** und **`recommendations`** in Plan und **Producer-Task** übernehmen oder den Verzicht kurz begründen. **`localhost:8049`** ist nur **Dev-Relais** (HTTP→mTLS zum VPS) für bestimmte MCP-Tools — **kein** Infrastructure-Sentinel.

**English (optional):** For substantial tasks, call MCP **`get_orchestrator_bootstrap`** with a short **`task_hint`** first; apply **`gaps`**/**`recommendations`** in plans and producer task prompts. Port **8049** is a local dev relay only, not fleet heartbeat.

---

## Kurz-Verweise

| Thema | Datei |
|--------|--------|
| Kanon-Tür („wo liegt was?“) | `KANON_EINSTIEG.md` |
| Voller Doku-Index | `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` |
| Verfassung / Orchestrator | `.cursorrules` |
| Projekt-Kurzkontext | `CLAUDE.md` |
| System-Payload / Eichung | `CORE_EICHUNG.md` |
| Resonanz-Anker / Workflow | `docs/00_STAMMDOKUMENTE/OMEGA_RESONANCE_ANCHOR.md` |

**Sprache:** Standard **Deutsch**; Code- und API-Namen unverändert.

---

## MCP / Skills

- **`user-omega-state-mcp`** (`src/scripts/mcp_omega_state.py`): u. a. **`get_orchestrator_bootstrap`**, **`list_canon_documents`**, **`query_canon_semantic`** (**Soll**, `core_canon`), **`query_operational_semantic`** (**Ist**, `core_operational`), **`get_episodic_history`**, **`record_event`**. Kompass: **`docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md`**. Bindung: **`docs/04_PROCESSES/CANON_REGISTRY_AGENT_BINDUNG.md`**. Regeln: **`.cursor/rules/9_ORCHESTRATOR_BOOTSTRAP_MCP.mdc`**, **`.cursor/rules/8_CANON_REGISTRY_PREFLIGHT.mdc`**. Skill: **`.cursor/skills/orchestrator-bootstrap-preflight/SKILL.md`**.
- **`core-chromadb`**: Beliebige Collections (`query_chromadb`) — Konfiguration **`mcp_remote_config.json`**. Collections z. B. `core_canon`, `core_operational` (nach den jeweiligen Ingest-Skripten). **Chroma = Vorschlag, kein Fakt** — **`zero_trust_notice`** steht in **jedem** `query_chromadb`-JSON (wie bei den State-MCP-Semantik-Tools); Details **`CANON_REGISTRY_AGENT_BINDUNG.md` §2**.
- **Abgrenzung:** MCP ist **KI↔Tool**-Schicht; die zentrale **HTTP-API-Drehscheibe** der Laufzeit ist davon getrennt — siehe **`docs/02_ARCHITECTURE/LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md`**.

Nach Änderungen am MCP-Skript: In Cursor den Server **OMEGA State** neu starten oder das Fenster neu laden.

---

## Visuelle Referenz (optional)

Architektur-Überblick: **`CORE_TESSERAKT.png`** (Repo-Root), sofern vorhanden.
