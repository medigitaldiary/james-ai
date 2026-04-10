-- Feedback table for James AI response ratings
CREATE TABLE IF NOT EXISTS message_feedback (
    id           BIGSERIAL PRIMARY KEY,
    message_id   TEXT        NOT NULL UNIQUE,   -- frontend-generated message UUID
    rating       TEXT        NOT NULL CHECK (rating IN ('up', 'down')),
    user_query   TEXT        NOT NULL DEFAULT '',
    content_hash TEXT        NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_rating     ON message_feedback (rating);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON message_feedback (created_at DESC);
