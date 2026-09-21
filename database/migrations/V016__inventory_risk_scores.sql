-- =============================================================================
-- ZivaStock Production Schema — V016
-- Transparent inventory risk scores
-- =============================================================================

CREATE TABLE IF NOT EXISTS inventory_risk_scores (
    id                  BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    location_id         BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    calculation_date    DATE NOT NULL,
    anomaly_score       NUMERIC(8, 4) NOT NULL DEFAULT 0,
    variance_score      NUMERIC(8, 4) NOT NULL DEFAULT 0,
    financial_value_score NUMERIC(8, 4) NOT NULL DEFAULT 0,
    stockout_score      NUMERIC(8, 4) NOT NULL DEFAULT 0,
    adjustment_score    NUMERIC(8, 4) NOT NULL DEFAULT 0,
    accuracy_score      NUMERIC(8, 4) NOT NULL DEFAULT 0,
    criticality_score   NUMERIC(8, 4) NOT NULL DEFAULT 0,
    total_score         NUMERIC(8, 4) NOT NULL DEFAULT 0 CHECK (total_score BETWEEN 0 AND 100),
    risk_level          VARCHAR(20) NOT NULL DEFAULT 'LOW'
        CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    abc_class           VARCHAR(1) CHECK (abc_class IS NULL OR abc_class IN ('A', 'B', 'C')),
    priority            VARCHAR(30) NOT NULL DEFAULT 'MONITOR',
    explanation         JSONB NOT NULL DEFAULT '[]'::jsonb,
    calculation_version VARCHAR(50) NOT NULL DEFAULT 'v1',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inventory_risk_product ON inventory_risk_scores(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_risk_location ON inventory_risk_scores(location_id);
CREATE INDEX IF NOT EXISTS idx_inventory_risk_date ON inventory_risk_scores(calculation_date);
CREATE INDEX IF NOT EXISTS idx_inventory_risk_total ON inventory_risk_scores(total_score);
CREATE INDEX IF NOT EXISTS idx_inventory_risk_level ON inventory_risk_scores(risk_level);
CREATE INDEX IF NOT EXISTS idx_inventory_risk_abc ON inventory_risk_scores(abc_class);
