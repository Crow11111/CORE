-- Migration: Add Tesserakt Facet Columns to multi_view_embeddings
-- Duale Topologie: Diese Spalten dienen als Cache in der int-Domaene.
-- Die primaere Vektor-Suche findet kuenftig in isolierten ChromaDB-Räumen statt.

ALTER TABLE multi_view_embeddings ADD COLUMN IF NOT EXISTS v_keywords vector(3072);
ALTER TABLE multi_view_embeddings ADD COLUMN IF NOT EXISTS v_semantics vector(3072);
ALTER TABLE multi_view_embeddings ADD COLUMN IF NOT EXISTS v_media vector(3072);

ALTER TABLE multi_view_embeddings ADD COLUMN IF NOT EXISTS v_keywords_768 vector(768);
ALTER TABLE multi_view_embeddings ADD COLUMN IF NOT EXISTS v_semantics_768 vector(768);
ALTER TABLE multi_view_embeddings ADD COLUMN IF NOT EXISTS v_media_768 vector(768);

COMMENT ON COLUMN multi_view_embeddings.v_keywords IS 'Tesserakt-Facette: Harte Keywords / Identifikatoren';
COMMENT ON COLUMN multi_view_embeddings.v_semantics IS 'Tesserakt-Facette: Semantische Zusammenfassung';
COMMENT ON COLUMN multi_view_embeddings.v_media IS 'Tesserakt-Facette: Modale/Mediale Deskriptoren';
