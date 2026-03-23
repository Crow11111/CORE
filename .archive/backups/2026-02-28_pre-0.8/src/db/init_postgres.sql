CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS predictive_matrix (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trigger_hash VARCHAR(64) NOT NULL,
    a_priori_weight NUMERIC(4,3) CHECK (a_priori_weight >= 0.0 AND a_priori_weight <= 1.0) NOT NULL,
    ex_post_delta NUMERIC(8,3) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictive_matrix_trigger_hash ON predictive_matrix(trigger_hash);
