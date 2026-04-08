# Migrationsplan: Kanon-Wissen in Datenbanken (Resonanz-Anker & Folge-Dokumente)

**Ziel:** Strukturierte, abfragbare **Spiegelung** von `OMEGA_RESONANCE_ANCHOR.md` und den darin genannten Pfaden in **PostgreSQL**; spätere Phasen: **Chroma/pgvector** für Semantik, **omega_events** nur für **episodische** Audit-Trails (bestehend).

**Nicht-Ziel:** Volltext aller Markdown-Dateien des Repos in PG duplizieren — das bleibt **Git + Filesystem** als Autorität; die DB hält **Metadaten, Hashes, Graph-Kanten**.

---

## Warum das sinnvoll ist

| Problem | Mit Registry-Tabelle |
|--------|----------------------|
| Agent liest nur Chat/Teildoku | SQL: „welche Kanon-Dateien sind registriert, wann zuletzt synchronisiert?“ |
| Drift Anker ↔ Platte | `body_sha256` ändert sich → Re-Sync / Alarm |
| `omega_events` überladen | Events = **Vorkommnisse**; Kanon = **Versionierte Dokument-Instanzen** (getrennte Tabelle) |
| Chroma ohne Anker-Filters | Metadaten `anchor_section`, `document_role` feeden später `type` / `source_collection` (Zero-State-Schema) |

---

## Phase 0 (sofort): PostgreSQL — `omega_canon_documents`

**Artefakt:** `src/db/migrations/001_omega_canon_documents.sql`

| Spalte | Zweck |
|--------|--------|
| `repo_path` | POSIX-Pfad relativ Repo-Root, UNIQUE |
| `document_role` | `anchor_root`, `referenced`, `executable`, `code` |
| `anchor_section` | z. B. `4`, `5`, `footer` — wo der Anker das Dokument erwähnt |
| `body_sha256` | SHA-256 des Dateiinhalts (Drift-Detektion) |
| `byte_size` | A6: Infrastruktur-Zähler als int |
| `last_synced_at` | Zeitpunkt des letzten Sync-Laufs |
| `metadata` | JSONB: optional `git_head`, `ingest_chroma_pending` |

**Anwendung der Migration:** `src/db/migrations/001_omega_canon_documents.sql` — manuell per `psql` **oder** idempotent beim ersten Lauf von `python -m src.scripts.sync_omega_canon_registry` (führt `CREATE IF NOT EXISTS` über denselben SSH/psql-Weg wie `omega_events` aus). Operator mit Root-Zugang zum VPS-Postgres vorausgesetzt.

---

## Phase 1 (umgesetzt): Sync-Skript

**Artefakt:** `python -m src.scripts.sync_omega_canon_registry`

- Liest `OMEGA_RESONANCE_ANCHOR.md`.
- Ermittelt referenzierte Pfade (Backticks, explizite `docs/…`, statische Liste Fußzeile §4–§5).
- Hasht jede existierende Datei, **UPSERT** per `ON CONFLICT (repo_path)`.

**Operator:** Nach größeren Doku-Änderungen oder vor Abnahme ausführen; optional in Session-Log vermerken.

---

## Phase 2 (umgesetzt): Chroma — Collection `core_canon`

- **Skript:** `python -m src.scripts.ingest_omega_canon_chroma` — liest **`omega_canon_documents`** per `list_canon_documents` (PG); wenn leer → Fallback wie Sync (**`--from-disk`** / Anker+Seeds).
- **Collection:** `core_canon` (Konstante `COLLECTION_CORE_CANON` in `chroma_client.py`); Default-Embedding **384** + `CrystalGridEngine.snap_to_grid`.
- **Metadaten (Zero-State-kompatibel):** `type=context`, `source_collection=core_canon`, `source_file`/`repo_path`, `chunk_index`, `anchor_section`, `document_role`, `body_sha256`, `date_added`.
- **Nach PG-Sync:** optional `OMEGA_CANON_CHROMA_AFTER_SYNC=1` — triggert Ingest nach erfolgreichem `sync_omega_canon_registry` (Chroma-Fehler → **Warnung**, PG bleibt OK).
- **Abfrage:** MCP **`query_canon_semantic`** / **`query_operational_semantic`** (`user-omega-state-mcp`) **oder** `query_chromadb` mit `collection_name=core_canon` bzw. `core_operational`.
- **Migration zu einheitlichem `zero_state_field`:** Backlog — aktuell eigene Collection wie `world_knowledge` / `mth_user_profile`.

### Phase 2b: `core_operational` (Ist, getrennt von Kanon)

- **Skript:** `python -m src.scripts.ingest_omega_operational_chroma` — liest **`docs/00_STAMMDOKUMENTE/KERNARBEITER_SURFACE_PATHS.yaml`** (kuratierte Pfade: Ports, Verkehrsplan, Landkarte, …).
- **Collection:** `COLLECTION_CORE_OPERATIONAL` = **`core_operational`** — bewusst **nicht** aus `omega_canon_documents`, damit **Plan ≠ Realität** semantisch nicht vermischt wird.
- **MCP:** **`query_operational_semantic`** (`user-omega-state-mcp`).
- **Doku:** **`docs/04_PROCESSES/KERNARBEITER_ORIENTIERUNG.md`**.

---

## Phase 3: MCP / Tools (umgesetzt / finalisiert)

- **Read-only:** **`list_canon_documents`**, **`get_episodic_history`** (bestehend).
- **Orchestrator-Bundle:** **`get_orchestrator_bootstrap`** — Kanon-Kurzliste, Event-Summaries, Erreichbarkeit VPS-MCP-HTTP; **8049** nur bei Env **`OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1`** (sonst `null` im JSON); **`gaps`**, **`recommendations`**, `task_hint`.
- **Heartbeat:** `InfrastructureSentinel` schreibt **`mcp-server`** in `core_infrastructure` (HTTP-„any response“ auf Host-Port **8001**).
- **Prozess + Rules:** `docs/04_PROCESSES/CANON_REGISTRY_AGENT_BINDUNG.md`, `.cursor/rules/8_CANON_REGISTRY_PREFLIGHT.mdc`, `.cursor/rules/9_ORCHESTRATOR_BOOTSTRAP_MCP.mdc` (`alwaysApply`).
- Optional: `record_event` nach Sync — weiterhin empfohlen.

---

## Abgrenzung

- **Secrets** nie in `omega_canon_documents.metadata`.
- **Git-Resonanz** (Ticket 9) spiegelt nur **Teilmengen** — die Registry **ersetzt** kein `git pull`; sie **dokumentiert**, welche Kanon-Pfade **explizit** am Anker hängen.

---

[PASS] Plan abgestimmt mit dualer Topologie (PG strukturiert, Chroma semantisch später).
