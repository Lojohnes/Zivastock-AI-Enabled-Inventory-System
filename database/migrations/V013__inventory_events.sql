-- =============================================================================
-- ZivaStock Production Schema — V013
-- Unified Inventory Events and Transaction Import Support
-- =============================================================================

CREATE TABLE IF NOT EXISTS inventory_events (
    id                  BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    location_id         BIGINT REFERENCES locations(id) ON DELETE SET NULL,
    event_type          VARCHAR(30) NOT NULL CHECK (event_type IN (
        'SALE', 'PURCHASE', 'RECEIPT', 'RETURN', 'TRANSFER', 'STOCKTAKE',
        'COUNT', 'ADJUSTMENT', 'WASTE', 'DAMAGE', 'PRICE_CHANGE',
        'LOCATION_CHANGE', 'OPENING_BALANCE', 'CLOSING_BALANCE'
    )),
    quantity            NUMERIC(18, 4) NOT NULL CHECK (quantity >= 0),
    unit_cost           NUMERIC(18, 4) CHECK (unit_cost IS NULL OR unit_cost >= 0),
    transaction_value   NUMERIC(18, 4),
    event_timestamp     TIMESTAMPTZ NOT NULL,
    user_id             BIGINT REFERENCES users(id) ON DELETE SET NULL,
    source_system       VARCHAR(50) NOT NULL,
    source_record_id    VARCHAR(150) NOT NULL,
    reference_number    VARCHAR(150),
    stocktake_session_id BIGINT REFERENCES stocktake_sessions(id) ON DELETE SET NULL,
    import_batch_id     BIGINT REFERENCES imports(id) ON DELETE SET NULL,
    is_validated        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_inventory_event_source_record UNIQUE (source_system, source_record_id)
);

CREATE INDEX IF NOT EXISTS idx_inventory_events_product ON inventory_events(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_events_location ON inventory_events(location_id);
CREATE INDEX IF NOT EXISTS idx_inventory_events_type ON inventory_events(event_type);
CREATE INDEX IF NOT EXISTS idx_inventory_events_timestamp ON inventory_events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_inventory_events_source ON inventory_events(source_system);
CREATE INDEX IF NOT EXISTS idx_inventory_events_reference ON inventory_events(reference_number);
CREATE INDEX IF NOT EXISTS idx_inventory_events_session ON inventory_events(stocktake_session_id);
CREATE INDEX IF NOT EXISTS idx_inventory_events_import ON inventory_events(import_batch_id);

ALTER TABLE imports DROP CONSTRAINT IF EXISTS imports_entity_type_check;
ALTER TABLE imports DROP CONSTRAINT IF EXISTS chk_imports_entity_type;
ALTER TABLE imports ADD CONSTRAINT chk_imports_entity_type CHECK (
    entity_type IN ('products', 'locations', 'users', 'counts', 'categories', 'inventory_events')
);

COMMENT ON TABLE inventory_events IS 'Canonical inventory movements from POS, ERP, stocktake, imports and simulator sources.';
COMMENT ON COLUMN inventory_events.source_record_id IS 'Stable source-system identifier used for idempotent ingestion.';
