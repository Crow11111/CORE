-- Multi-View Embedding Schema (CORE B* -- Polytopische Repraesentation)
-- pgvector 0.8.2 auf atlas_postgres_state (VPS)
-- Ein Dokument, 6 Perspektiven, Konvergenz messbar.

CREATE TABLE IF NOT EXISTS multi_view_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id VARCHAR(128) NOT NULL,
    document TEXT NOT NULL,
    source_collection VARCHAR(64),

    v_math     vector(768),
    v_physics  vector(768),
    v_philo    vector(768),
    v_bio      vector(768),
    v_info     vector(768),
    v_narr     vector(768),

    convergence_score FLOAT,
    convergence_pairs JSONB,

    e6_anchor_id INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_mv_doc_id ON multi_view_embeddings (doc_id);
CREATE INDEX IF NOT EXISTS idx_mv_convergence ON multi_view_embeddings (convergence_score DESC);
CREATE INDEX IF NOT EXISTS idx_mv_source ON multi_view_embeddings (source_collection);

CREATE INDEX IF NOT EXISTS idx_mv_math    ON multi_view_embeddings USING ivfflat (v_math    vector_cosine_ops) WITH (lists = 13);
CREATE INDEX IF NOT EXISTS idx_mv_physics ON multi_view_embeddings USING ivfflat (v_physics vector_cosine_ops) WITH (lists = 13);
CREATE INDEX IF NOT EXISTS idx_mv_philo   ON multi_view_embeddings USING ivfflat (v_philo   vector_cosine_ops) WITH (lists = 13);
CREATE INDEX IF NOT EXISTS idx_mv_bio     ON multi_view_embeddings USING ivfflat (v_bio     vector_cosine_ops) WITH (lists = 13);
CREATE INDEX IF NOT EXISTS idx_mv_info    ON multi_view_embeddings USING ivfflat (v_info    vector_cosine_ops) WITH (lists = 13);
CREATE INDEX IF NOT EXISTS idx_mv_narr    ON multi_view_embeddings USING ivfflat (v_narr    vector_cosine_ops) WITH (lists = 13);
