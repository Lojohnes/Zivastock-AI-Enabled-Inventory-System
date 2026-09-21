-- =============================================================================
-- ZivaStock Production Schema — V015
-- Model registry and anomaly detection results
-- =============================================================================

CREATE TABLE IF NOT EXISTS model_versions (
    id                  BIGSERIAL PRIMARY KEY,
    model_name          VARCHAR(100) NOT NULL,
    algorithm           VARCHAR(100) NOT NULL,
    version             VARCHAR(50) NOT NULL,
    dataset_version     VARCHAR(100),
    feature_set_version VARCHAR(100),
    features            JSONB NOT NULL DEFAULT '[]'::jsonb,
    hyperparameters     JSONB NOT NULL DEFAULT '{}'::jsonb,
    training_start      DATE,
    training_end        DATE,
    evaluation_metrics  JSONB NOT NULL DEFAULT '{}'::jsonb,
    artifact_path       VARCHAR(512),
    status              VARCHAR(30) NOT NULL DEFAULT 'evaluated'
        CHECK (status IN ('draft', 'trained', 'evaluated', 'selected', 'retired')),
    created_by          BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_model_versions_name ON model_versions(model_name);
CREATE INDEX IF NOT EXISTS idx_model_versions_status ON model_versions(status);

CREATE TABLE IF NOT EXISTS anomaly_results (
    id                    BIGSERIAL PRIMARY KEY,
    product_id            BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    location_id           BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    feature_date          DATE NOT NULL,
    model_version_id      BIGINT REFERENCES model_versions(id) ON DELETE SET NULL,
    algorithm             VARCHAR(100) NOT NULL,
    anomaly_flag          INTEGER NOT NULL DEFAULT 0 CHECK (anomaly_flag IN (0, 1)),
    anomaly_score         NUMERIC(8, 4) NOT NULL DEFAULT 0 CHECK (anomaly_score BETWEEN 0 AND 100),
    risk_level            VARCHAR(20) NOT NULL DEFAULT 'LOW'
        CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    threshold_used        NUMERIC(8, 4),
    evidence              JSONB NOT NULL DEFAULT '[]'::jsonb,
    feature_contributions JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomaly_results_product ON anomaly_results(product_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_location ON anomaly_results(location_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_date ON anomaly_results(feature_date);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_model ON anomaly_results(model_version_id);
