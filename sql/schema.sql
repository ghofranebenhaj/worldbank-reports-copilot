CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_file TEXT UNIQUE NOT NULL,
    ingested_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page INT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,
    chunk_config TEXT NOT NULL,
    embedding vector(384),
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING GIN (tsv);
CREATE INDEX IF NOT EXISTS chunks_config_idx ON chunks (chunk_config);

CREATE TABLE IF NOT EXISTS query_log (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    provider TEXT,
    retrieved INT,
    latency_ms INT,
    answered BOOLEAN,
    created_at TIMESTAMP DEFAULT now()
);
