-- OMEGA Kanon-Dokument-Registry (Resonanz-Anker + referenzierte Artefakte)
-- Vector: 2210 | Delta: 0.049
-- Anwendung: gleiche Postgres-Instanz wie omega_events (VPS pgvector / atlas_postgres_state).
-- Idempotent: CREATE IF NOT EXISTS

CREATE TABLE IF NOT EXISTS omega_canon_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_path TEXT NOT NULL,
    document_role TEXT NOT NULL DEFAULT 'referenced',
    anchor_section TEXT,
    title TEXT,
    body_sha256 CHAR(64) NOT NULL,
    byte_size INTEGER NOT NULL CHECK (byte_size >= 0),
    last_synced_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT omega_canon_documents_repo_path_key UNIQUE (repo_path)
);

CREATE INDEX IF NOT EXISTS idx_omega_canon_documents_role
    ON omega_canon_documents (document_role);

CREATE INDEX IF NOT EXISTS idx_omega_canon_documents_section
    ON omega_canon_documents (anchor_section);

CREATE INDEX IF NOT EXISTS idx_omega_canon_documents_synced
    ON omega_canon_documents (last_synced_at DESC);
