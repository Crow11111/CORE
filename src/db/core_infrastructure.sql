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
