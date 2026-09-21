-- =============================================================================
-- ZivaStock Production Schema — V018
-- Explainable AI recommendations and human decisions
-- =============================================================================

CREATE TABLE IF NOT EXISTS ai_recommendations (
    id                  BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    location_id         BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    recommendation_type VARCHAR(40) NOT NULL,
    recommendation_text TEXT NOT NULL,
    priority            VARCHAR(30) NOT NULL DEFAULT 'MONITOR',
    confidence_score    NUMERIC(6, 2) CHECK (confidence_score IS NULL OR confidence_score BETWEEN 0 AND 100),
    evidence            JSONB NOT NULL DEFAULT '[]'::jsonb,
    expected_impact     JSONB NOT NULL DEFAULT '{}'::jsonb,
    model_version_id    BIGINT REFERENCES model_versions(id) ON DELETE SET NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'OVERRIDDEN', 'COMPLETED', 'EXPIRED')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_ai_recommendations_product ON ai_recommendations(product_id);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_location ON ai_recommendations(location_id);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_type ON ai_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_priority ON ai_recommendations(priority);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_status ON ai_recommendations(status);

CREATE TABLE IF NOT EXISTS recommendation_decisions (
    id                  BIGSERIAL PRIMARY KEY,
    recommendation_id   BIGINT NOT NULL REFERENCES ai_recommendations(id) ON DELETE CASCADE,
    decision            VARCHAR(20) NOT NULL CHECK (decision IN ('APPROVED', 'REJECTED', 'OVERRIDDEN')),
    decided_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    decision_reason     TEXT,
    override_flag       INTEGER NOT NULL DEFAULT 0 CHECK (override_flag IN (0, 1)),
    decided_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recommendation_decisions_recommendation ON recommendation_decisions(recommendation_id);

CREATE TABLE IF NOT EXISTS recommendation_outcomes (
    id                  BIGSERIAL PRIMARY KEY,
    recommendation_id   BIGINT NOT NULL REFERENCES ai_recommendations(id) ON DELETE CASCADE,
    actual_action       VARCHAR(100),
    outcome_status      VARCHAR(30) NOT NULL CHECK (outcome_status IN ('PENDING', 'SUCCESS', 'PARTIAL', 'FAILED', 'NOT_APPLICABLE')),
    actual_result       TEXT,
    variance_after_action NUMERIC(18, 4),
    stockout_avoided    INTEGER CHECK (stockout_avoided IS NULL OR stockout_avoided IN (0, 1)),
    recorded_by         BIGINT REFERENCES users(id) ON DELETE SET NULL,
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recommendation_outcomes_recommendation ON recommendation_outcomes(recommendation_id);
