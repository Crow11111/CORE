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

## Phase 2 (Backlog): Chroma / zero_state_field

- Pro `omega_canon_documents`-Zeile optional **Chunk-Ingest** in eine Collection `core_canon` (oder Migration zu `zero_state_field` laut `ZERO_STATE_FIELD_SCHEMA.md`).
- Metadaten: `type=context`, `source_collection=core_canon`, `anchor_section`, `repo_path`.
- **Nicht** parallel starten, bevor Phase 1 stabil grün ist.

---

## Phase 3: MCP / Tools (umgesetzt / finalisiert)

- **Read-only:** **`list_canon_documents`**, **`get_episodic_history`** (bestehend).
- **Orchestrator-Bundle:** **`get_orchestrator_bootstrap`** — Kanon-Kurzliste, Event-Summaries, Erreichbarkeit VPS-MCP-HTTP; **8049** nur bei Env **`OMEGA_BOOTSTRAP_PROBE_LOCAL_PROXY=1`** (sonst `null` im JSON); **`gaps`**, **`recommendations`**, `task_hint`.
- **Heartbeat:** `InfrastructureSentinel` schreibt **`mcp-server`** in `core_infrastructure` (HTTP-„any response“ auf Host-Port **8001**).
- **Prozess + Rule:** `docs/04_PROCESSES/CANON_REGISTRY_AGENT_BINDUNG.md`, `.cursor/rules/8_CANON_REGISTRY_PREFLIGHT.mdc`.
- Optional: `record_event` nach Sync — weiterhin empfohlen.

---

## Abgrenzung

- **Secrets** nie in `omega_canon_documents.metadata`.
- **Git-Resonanz** (Ticket 9) spiegelt nur **Teilmengen** — die Registry **ersetzt** kein `git pull`; sie **dokumentiert**, welche Kanon-Pfade **explizit** am Anker hängen.

---

[PASS] Plan abgestimmt mit dualer Topologie (PG strukturiert, Chroma semantisch später).
