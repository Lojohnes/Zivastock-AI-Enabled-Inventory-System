-- =============================================================================
-- ZivaStock Production Schema — V017
-- Forecast results and stockout/overstock exposure
-- =============================================================================

CREATE TABLE IF NOT EXISTS forecast_results (
    id                  BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    location_id         BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    model_version_id    BIGINT REFERENCES model_versions(id) ON DELETE SET NULL,
    model_algorithm     VARCHAR(50) NOT NULL,
    forecast_date       DATE NOT NULL,
    horizon_days        INTEGER NOT NULL DEFAULT 7,
    predicted_demand    NUMERIC(18, 4) NOT NULL,
    lower_bound         NUMERIC(18, 4),
    upper_bound         NUMERIC(18, 4),
    actual_demand       NUMERIC(18, 4),
    evaluation_metrics  JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_forecast_results_product ON forecast_results(product_id);
CREATE INDEX IF NOT EXISTS idx_forecast_results_location ON forecast_results(location_id);
CREATE INDEX IF NOT EXISTS idx_forecast_results_model ON forecast_results(model_version_id);
CREATE INDEX IF NOT EXISTS idx_forecast_results_date ON forecast_results(forecast_date);

CREATE TABLE IF NOT EXISTS inventory_exposures (
    id                  BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    location_id         BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    calculation_date    DATE NOT NULL,
    forecast_model      VARCHAR(50) NOT NULL,
    current_quantity    NUMERIC(18, 4) NOT NULL,
    predicted_daily_demand NUMERIC(18, 4) NOT NULL,
    safety_stock        NUMERIC(18, 4) NOT NULL DEFAULT 0,
    days_until_stockout NUMERIC(18, 4),
    stockout_date       DATE,
    stockout_risk       VARCHAR(20) NOT NULL DEFAULT 'LOW'
        CHECK (stockout_risk IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    excess_quantity     NUMERIC(18, 4) NOT NULL DEFAULT 0,
    slow_moving         INTEGER NOT NULL DEFAULT 0 CHECK (slow_moving IN (0, 1)),
    non_moving          INTEGER NOT NULL DEFAULT 0 CHECK (non_moving IN (0, 1)),
    explanation         JSONB NOT NULL DEFAULT '[]'::jsonb,
    calculation_version VARCHAR(50) NOT NULL DEFAULT 'v1',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inventory_exposures_product ON inventory_exposures(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_exposures_location ON inventory_exposures(location_id);
CREATE INDEX IF NOT EXISTS idx_inventory_exposures_date ON inventory_exposures(calculation_date);
