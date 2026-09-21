-- =============================================================================
-- ZivaStock Production Schema — V014
-- Data quality tracking and reproducible feature snapshots
-- =============================================================================

CREATE TABLE IF NOT EXISTS data_quality_batches (
    id                  BIGSERIAL PRIMARY KEY,
    import_batch_id     BIGINT REFERENCES imports(id) ON DELETE SET NULL,
    dataset_type        VARCHAR(50) NOT NULL,
    source_system       VARCHAR(50) NOT NULL,
    quality_score       NUMERIC(6, 2) NOT NULL CHECK (quality_score BETWEEN 0 AND 100),
    total_records       INTEGER NOT NULL DEFAULT 0 CHECK (total_records >= 0),
    valid_records       INTEGER NOT NULL DEFAULT 0 CHECK (valid_records >= 0),
    invalid_records     INTEGER NOT NULL DEFAULT 0 CHECK (invalid_records >= 0),
    duplicate_records   INTEGER NOT NULL DEFAULT 0 CHECK (duplicate_records >= 0),
    missing_value_count INTEGER NOT NULL DEFAULT 0 CHECK (missing_value_count >= 0),
    issue_summary       JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_data_quality_batches_import ON data_quality_batches(import_batch_id);

CREATE TABLE IF NOT EXISTS data_quality_issues (
    id                  BIGSERIAL PRIMARY KEY,
    batch_id            BIGINT NOT NULL REFERENCES data_quality_batches(id) ON DELETE CASCADE,
    record_reference    VARCHAR(150),
    row_number          INTEGER,
    issue_type          VARCHAR(50) NOT NULL,
    field_name          VARCHAR(100),
    severity            VARCHAR(20) NOT NULL DEFAULT 'error' CHECK (severity IN ('info', 'warning', 'error')),
    description         TEXT NOT NULL,
    raw_value           JSONB,
    resolved            VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (resolved IN ('open', 'resolved', 'ignored')),
    resolution_note     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_data_quality_issues_batch ON data_quality_issues(batch_id);
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_reference ON data_quality_issues(record_reference);
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_type ON data_quality_issues(issue_type);

CREATE TABLE IF NOT EXISTS inventory_feature_snapshots (
    id                  BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    location_id         BIGINT REFERENCES locations(id) ON DELETE CASCADE,
    feature_date        DATE NOT NULL,
    lookback_days       INTEGER NOT NULL DEFAULT 30,
    feature_set_version VARCHAR(50) NOT NULL DEFAULT 'v1',
    current_quantity    NUMERIC(18, 4) NOT NULL DEFAULT 0,
    average_quantity    NUMERIC(18, 4) NOT NULL DEFAULT 0,
    minimum_quantity    NUMERIC(18, 4) NOT NULL DEFAULT 0,
    maximum_quantity    NUMERIC(18, 4) NOT NULL DEFAULT 0,
    daily_sales         NUMERIC(18, 4) NOT NULL DEFAULT 0,
    weekly_sales        NUMERIC(18, 4) NOT NULL DEFAULT 0,
    sales_velocity      NUMERIC(18, 4) NOT NULL DEFAULT 0,
    demand_variability  NUMERIC(18, 4) NOT NULL DEFAULT 0,
    sales_value         NUMERIC(18, 4) NOT NULL DEFAULT 0,
    inventory_value     NUMERIC(18, 4) NOT NULL DEFAULT 0,
    variance_quantity   NUMERIC(18, 4) NOT NULL DEFAULT 0,
    variance_percentage NUMERIC(18, 4) NOT NULL DEFAULT 0,
    historical_variance NUMERIC(18, 4) NOT NULL DEFAULT 0,
    adjustment_frequency INTEGER NOT NULL DEFAULT 0,
    count_disagreement  INTEGER NOT NULL DEFAULT 0,
    days_of_inventory   NUMERIC(18, 4),
    abc_class           VARCHAR(1),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_inventory_feature_snapshot UNIQUE (product_id, location_id, feature_date, feature_set_version)
);

CREATE INDEX IF NOT EXISTS idx_inventory_features_product ON inventory_feature_snapshots(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_features_location ON inventory_feature_snapshots(location_id);
CREATE INDEX IF NOT EXISTS idx_inventory_features_date ON inventory_feature_snapshots(feature_date);
