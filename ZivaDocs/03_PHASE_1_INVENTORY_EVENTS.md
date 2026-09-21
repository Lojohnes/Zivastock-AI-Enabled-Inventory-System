# Phase 1 — Unified Inventory Events and Transaction Ingestion

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 1 adds the historical operational-data foundation required by the later AI modules. It does not implement anomaly detection or forecasting yet. It converts POS/ERP-style records, stock movements and future Sage Evolution exports into a canonical inventory-event structure.

## Implemented components

### Canonical event model

Added:

- `backend/app/models/inventory_event.py`
- `backend/alembic/versions/005_inventory_events.py`
- `database/migrations/V013__inventory_events.sql`

The model supports:

```text
SALE
PURCHASE
RECEIPT
RETURN
TRANSFER
STOCKTAKE
COUNT
ADJUSTMENT
WASTE
DAMAGE
PRICE_CHANGE
LOCATION_CHANGE
OPENING_BALANCE
CLOSING_BALANCE
```

Each event records:

- Product
- Optional location
- Event type
- Quantity
- Unit cost
- Transaction value
- Event timestamp
- User where available
- Source system
- Stable source-record identifier
- Reference number
- Optional stocktake session
- Optional import batch
- Validation state
- Creation timestamp

The `(source_system, source_record_id)` unique constraint provides the first idempotency boundary for imported POS/ERP records.

### Transaction ingestion service

Added:

- `backend/app/services/inventory_event_service.py`

The service:

1. Accepts a pandas DataFrame
2. Applies a configurable source-column mapping
3. Validates event types
4. Validates numeric quantities and costs
5. Parses timestamps
6. Resolves products by ID, barcode, SKU or product code
7. Resolves locations by ID or name
8. Detects duplicate source records
9. Persists valid records in one transaction
10. Returns accepted, duplicate and rejected counts with row-level errors

### API endpoint

Added:

```text
POST /api/v1/inventory-events/ingest
```

The endpoint accepts CSV or Excel files and requires:

- `source_system`
- Optional `mapping_json`
- Authenticated user

Example mapping:

```json
{
  "source_record_id": "TransactionNo",
  "barcode": "ItemCode",
  "event_type": "MovementType",
  "quantity": "Qty",
  "event_timestamp": "TransactionDate"
}
```

The endpoint creates an import batch with entity type `inventory_events`, processes the records and updates batch status to `completed`, `completed_with_errors` or `failed`.

### Transaction simulator

Added:

- `backend/app/services/transaction_simulator.py`
- `backend/scripts/generate_transaction_dataset.py`

The simulator generates deterministic POS/ERP-style CSV data using a fixed seed and fixed default start date. Supported scenarios are:

- `normal`
- `high_demand`
- `abnormal_adjustment`
- `stock_discrepancy`
- `supplier_delay`

Example:

```powershell
cd backend
python scripts\generate_transaction_dataset.py `
  --days 30 `
  --scenario abnormal_adjustment `
  --seed 42 `
  --output ..\imports\simulated_transactions.csv
```

All generated data is simulated and must not be described as institutional or Sage data.

## Database migration process

The project has two migration representations:

1. PostgreSQL SQL migrations under `database/migrations`
2. Alembic migrations under `backend/alembic/versions`

Phase 1 adds both representations:

- `V013__inventory_events.sql`
- Alembic revision `005`

The current Alembic head is:

```text
005 (head)
```

Apply the migration from the backend directory with:

```powershell
$env:DEBUG='True'
python -m alembic upgrade head
```

The migration must be applied before using the live ingestion endpoint against a database that predates Phase 1.

## Data-flow position

```text
CSV/Excel/API source
        ↓
Import parser
        ↓
Column mapping
        ↓
Validation
        ↓
Product/location resolution
        ↓
Duplicate detection
        ↓
InventoryEvent records
        ↓
Future feature engineering and AI models
```

## Deliberate scope decisions

- The existing product import process remains unchanged.
- The existing physical stocktake and reconciliation workflow remains unchanged.
- The event model stores quantities as non-negative magnitudes. Event semantics are represented by `event_type`; future feature engineering will assign movement direction when constructing stock-balance features.
- The event ingestion endpoint is synchronous for the initial research prototype. Background processing can be introduced for larger institutional exports.
- The simulator does not attempt to become a complete POS. It is only a controlled, reproducible experimental data source.

## Verification

Phase 1 verification includes:

- Backend test suite: `14 passed`
- Python compilation: passed
- Alembic head discovery: `005 (head)`
- Simulator CLI generation: passed
- Ingestion service test covering product resolution, duplicate detection and rejection
- Simulator reproducibility and scenario-injection tests

Non-blocking warnings remain in the existing project for Pydantic deprecations, SQLAlchemy's legacy `declarative_base` import and frontend/Android build warnings.

## Next phase

Phase 2 should build the data-quality and feature-engineering layers on top of `inventory_events`. It should calculate quality scores, persist row-level data-quality issues and generate leakage-safe feature snapshots for anomaly detection and forecasting experiments.
