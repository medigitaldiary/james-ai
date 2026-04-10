-- Run this once against your Neon DB to set up the schema

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- KB files table (tracks uploaded PDFs and scraped pages)
CREATE TABLE IF NOT EXISTS kb_files (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    size        INTEGER NOT NULL DEFAULT 0,
    source      TEXT NOT NULL CHECK (source IN ('pdf', 'web')),
    url         TEXT,
    status      TEXT NOT NULL DEFAULT 'ready' CHECK (status IN ('uploading', 'ready', 'error')),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Documents table (chunks with embeddings)
CREATE TABLE IF NOT EXISTS documents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kb_file_id  UUID NOT NULL REFERENCES kb_files(id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    embedding   vector(768),
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- IVFFlat index for fast cosine similarity search
-- (recreate after bulk inserts for best performance)
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Index for fast file lookups
CREATE INDEX IF NOT EXISTS documents_kb_file_id_idx ON documents(kb_file_id);
CREATE INDEX IF NOT EXISTS kb_files_source_idx ON kb_files(source);
