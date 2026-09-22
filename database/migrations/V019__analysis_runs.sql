-- =============================================================================
-- ZivaStock Production Schema — V019
-- Analysis-run scoping for replacing Command Centre datasets without deleting history
-- =============================================================================

CREATE TABLE IF NOT EXISTS analysis_runs (
    id            BIGSERIAL PRIMARY KEY,
    analysis_key  VARCHAR(100) NOT NULL UNIQUE,
    analysis_type VARCHAR(30) NOT NULL,
    reference_id  VARCHAR(100),
    status        VARCHAR(20) NOT NULL DEFAULT 'COMPLETED'
        CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    created_by    BIGINT REFERENCES users(id) ON DELETE SET NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_analysis_runs_key ON analysis_runs(analysis_key);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_type ON analysis_runs(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_reference ON analysis_runs(reference_id);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_started ON analysis_runs(started_at);

ALTER TABLE anomaly_results ADD COLUMN IF NOT EXISTS analysis_key VARCHAR(100);
ALTER TABLE inventory_risk_scores ADD COLUMN IF NOT EXISTS analysis_key VARCHAR(100);
ALTER TABLE forecast_results ADD COLUMN IF NOT EXISTS analysis_key VARCHAR(100);
ALTER TABLE inventory_exposures ADD COLUMN IF NOT EXISTS analysis_key VARCHAR(100);
ALTER TABLE ai_recommendations ADD COLUMN IF NOT EXISTS analysis_key VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_anomaly_results_analysis_key ON anomaly_results(analysis_key);
CREATE INDEX IF NOT EXISTS idx_inventory_risk_analysis_key ON inventory_risk_scores(analysis_key);
CREATE INDEX IF NOT EXISTS idx_forecast_results_analysis_key ON forecast_results(analysis_key);
CREATE INDEX IF NOT EXISTS idx_inventory_exposures_analysis_key ON inventory_exposures(analysis_key);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_analysis_key ON ai_recommendations(analysis_key);
