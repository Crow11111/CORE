-- CORE Infrastructure 2D Integer-Membrane
-- Vector: 2210 | Resonance: 0221 | Delta: 0.049

CREATE TABLE IF NOT EXISTS core_infrastructure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_name TEXT NOT NULL, -- Dreadnought, Scout, VPS
    service_name TEXT NOT NULL,
    port INTEGER,
    url TEXT,
    purpose TEXT,
    status TEXT DEFAULT 'inactive', -- active, inactive, unknown
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(node_name, service_name)
);

-- Index für schnellere Status-Abfragen
CREATE INDEX IF NOT EXISTS idx_core_infra_status ON core_infrastructure(status);
CREATE INDEX IF NOT EXISTS idx_core_infra_node ON core_infrastructure(node_name);

-- Episodischer Event-Stream (diskrete Kausalität / Int-Domäne, A6).
-- Schreibpfad: INSERT nur via record_event; gezieltes DELETE nur durch Apoptose-Operator (Phase 2).
CREATE TABLE IF NOT EXISTS omega_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agent_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    content JSONB NOT NULL DEFAULT '{}'::jsonb,
    memory_hash TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_omega_events_ts ON omega_events ("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_omega_events_agent ON omega_events (agent_id);
CREATE INDEX IF NOT EXISTS idx_omega_events_type ON omega_events (event_type);

-- Ingest-Perimeter-Queue (Ticket 12): transaktional, FOR UPDATE SKIP LOCKED.
-- priority_float / confidence: Resonanzdomäne (A6); DB speichert DOUBLE PRECISION.
CREATE TABLE IF NOT EXISTS omega_ingest_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    priority_float DOUBLE PRECISION NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'failed', 'done')),
    trace_id TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_omega_ingest_queue_dequeue
    ON omega_ingest_queue (status, priority_float DESC, created_at ASC)
    WHERE status = 'pending';

CREATE UNIQUE INDEX IF NOT EXISTS idx_omega_ingest_queue_trace_id_active
    ON omega_ingest_queue (trace_id)
    WHERE status IN ('pending', 'processing');

-- Kanon-Dokument-Registry (Resonanz-Anker + referenzierte Pfade); vollständig auch unter src/db/migrations/001_omega_canon_documents.sql
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
