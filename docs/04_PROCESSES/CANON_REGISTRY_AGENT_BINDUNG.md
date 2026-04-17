# Kanon-Registry (`omega_canon_documents`) — Agenten-Bindung

**Problem:** Daten in PostgreSQL haben **keinen Effekt**, wenn niemand sie **abruft**. Die Tabelle ersetzt weder Chat-Kontext noch Dateizugriff — sie ist ein **expliziter Index**.

---

## 1. Säulen (zusammen wirksam)

| Säule | Was | Wer |
|-------|-----|-----|
| **MCP-Tool** | `list_canon_documents` — JSON-Liste aus PG (Pfade, Rollen, Hashes, `last_synced_at`) | Jeder Agent mit **user-omega-state-mcp** |
| **MCP-Tool (empfohlen 1× pro größerer Aufgabe)** | **`get_orchestrator_bootstrap`** — Kanon-Kurzliste + letzte `omega_events` + VPS-MCP-HTTP + optional **8049** nur bei Env `OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1` (Default: ungeprüft/`null`) + **`gaps`** + **`recommendations`**; optional `task_hint` | Orchestrator / Producer Pre-Flight |
| **Chroma Soll** | **`core_canon`** — **`ingest_omega_canon_chroma`** (Anker-Registry) | Plan/Kanon semantisch |
| **Chroma Ist** | **`core_operational`** — **`ingest_omega_operational_chroma`** (`KERNARBEITER_SURFACE_PATHS.yaml`) | Ports, Kong, Knoten, Messbarkeit — getrennt von Soll |
| **MCP Semantik Soll** | **`query_canon_semantic`** → `core_canon` | Kanon-Fragen |
| **MCP Semantik Ist** | **`query_operational_semantic`** → `core_operational` | Schnittstellen-/Betriebs-Fragen |
| **MCP Chroma generisch** | **`query_chromadb`** (`core-chromadb`) mit `collection_name=core_canon` oder `core_operational` | Beliebige Collections |
| **Prozess** | Vor größeren Infra-/Architektur-Tasks: **`get_orchestrator_bootstrap`** oder `list_canon_documents` | Orchestrator briefings / Producer pre-flight |
| **Regel** | `.cursor/rules/8_CANON_REGISTRY_PREFLIGHT.mdc` — wann Pflicht, wann empfohlen | Cursor lädt Rules bei relevanten Dateien |

---

## 2. Zero-Trust: Chroma-Treffer sind **keine** Fakten

**Immer:** Antworten von **`query_canon_semantic`**, **`query_operational_semantic`** und **`query_chromadb`** sind **Ähnlichkeitsvorschläge** im Embedding-Raum — **nicht** bewiesene Aussagen.

**Pflicht vor „Fakt“:** Metadatum **`repo_path`** / **`source_file`** → Datei im Workspace öffnen oder `@Pfad`; bei Ports/Zahlen → **`VPS_HOST_PORT_CONTRACT.md`**, **`vps_public_ports.py`**, **`verify_vps_stack`** o. ä.

Bei **`query_canon_semantic`**, **`query_operational_semantic`** (`user-omega-state-mcp`) und **`query_chromadb`** (`core-chromadb`, `mcp_core_chroma_stdio.py`) steht im JSON immer das Feld **`zero_trust_notice`** (gemeinsamer Text: `src/config/chroma_zero_trust_notice.py`).

---

## 3. A5 und Chroma — verschiedene Dimensionsebenen

**A5** gilt im Projekt für die **Resonanzdomäne**: Zustände, die sich auf einer Skala zwischen **„aus“ und „an“** bewegen (typisch Werte **nahe [0, 1]** — Trust, Delta, Schwellen, nicht die Integer-Infrastruktur). Dort sind **`0.0`**, **`1.0`**, **`0.5`** als **Resonanz-Zustand** verboten; stattdessen z. B. **`0.049`**, **`0.49`/`0.51`** (siehe Axiome / `core_state`).

**Chroma** lebt in einem **anderen Raum**: z. B. **hundertdimensionale Embeddings** und Distanzen für Retrieval. Das ist **keine** Resonanzskala im Sinne von A5 — das **A5-Regelwerk ist dort sachlich nicht anwendbar** („nichtssagend“ für diese Ebene). Es geht nicht um „A5 verletzt ja/nein“ beim bloßen Querying, sondern um **falsche Domänenvermischung** nur dann, wenn jemand **bewusst** Größen aus dem Embedding-Raum in **benannte CORE-Resonanzvariablen** übersetzt, **ohne** die Engine-Regeln — das ist ein Integrationsfehler, nicht „Chroma ist illegal“.

---

## 4. Was das Tool **nicht** leistet

- Kein Volltext der Dateien (dafür: Workspace / `@Pfad`).
- Keine eingebaute semantische Suche im PG-Tool — dafür **`core_canon`** / **`core_operational`** + MCP **`query_canon_semantic`** / **`query_operational_semantic`** (bzw. **`query_chromadb`**).
- Kein Ersatz für `get_episodic_history` (Ereignisse vs. Kanon-Metadaten).

---

## 5. Orchestrator (Ring 0)

- Beim Entwurf von **Task**-Prompts für VPS/Kong/MASTER: eine Zeile **„Pre-Flight: MCP `list_canon_documents`“** oder die Kurz-Zusammenfassung aus dem letzten Sync in den Prompt kopieren (ohne Secrets).
- Nach Anker-/Kanon-Änderungen: **`sync_omega_canon_registry`** anstoßen (Producer), dann **`record_event`** mit Kurzfassung.

---

## 6. MCP-Server neu laden

Nach Code-Änderungen am MCP: Cursor **MCP neu starten** / Fenster neu, damit neue Tools (z. B. `get_orchestrator_bootstrap`, `list_canon_documents`) in der Tool-Liste erscheinen.

## 7. Semantik: zwei Chroma-Collections (Soll vs. Ist)

- **Soll (`core_canon`):** nach PG-Sync **`python -m src.scripts.ingest_omega_canon_chroma`** (oder `OMEGA_CANON_CHROMA_AFTER_SYNC=1`). MCP **`query_canon_semantic`**.
- **Ist (`core_operational`):** **`python -m src.scripts.ingest_omega_operational_chroma`** (Quelle: **`docs/00_STAMMDOKUMENTE/KERNARBEITER_SURFACE_PATHS.yaml`**). MCP **`query_operational_semantic`**.
- **Orientierung:** **`docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md`** — wann welche Schicht, Drift-Regel.
- Alternativ **`query_chromadb`** mit `collection_name` — **ergänzt** PG/Dateien, ersetzt keine SSoT-Verifikation.

## 8. Abgrenzung: Sentinel vs. 8049

- **InfrastructureSentinel** (`infrastructure_heartbeat.py`) prüft **kein** `127.0.0.1` und **keinen** 8049 — nur von VPS/Scout/Dreadnought aus sichtbare Endpunkte.
- **localhost:8049** (`state_mtls_proxy`): Relais auf der **Dev-Workstation** für MCP → HTTPS+mTLS zum VPS; unabhängig vom Sentinel.

---

[PASS] Bindung dokumentiert; technische Schnittstelle = MCP + Sync-Skript.
