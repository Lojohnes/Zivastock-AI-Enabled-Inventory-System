# Phase 2 — Data Quality and Feature Engineering

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 2 prepares the unified inventory-event data for later anomaly detection, risk scoring and forecasting. It adds two research-critical capabilities:

1. A measurable data-quality pipeline with persisted issue records.
2. A reproducible feature-engineering pipeline with versioned feature snapshots.

No anomaly-detection or forecasting model has been added yet.

## Implemented components

### Data-quality persistence

Added:

- `backend/app/models/data_quality.py`
- Alembic revision `006_quality_and_features.py`
- `database/migrations/V014__quality_and_features.sql`

The data-quality model contains:

```text
data_quality_batches
--------------------
quality_score
total_records
valid_records
invalid_records
duplicate_records
missing_value_count
issue_summary
```

and:

```text
data_quality_issues
--------------------
record_reference
row_number
issue_type
field_name
severity
description
raw_value
resolved
resolution_note
```

This allows a quality score to be presented together with the reasons for that score.

### Quality checks

Added:

- `backend/app/services/data_quality_service.py`

The service checks:

- Missing required fields
- Unsupported event types
- Non-numeric quantities
- Negative quantities
- Invalid timestamps
- Future timestamps
- Duplicate records within the current dataset
- Duplicate records already stored for the source system
- Missing product identifiers
- Unresolved products
- Unresolved locations

The current quality score is calculated as the percentage of records that are valid and non-duplicate. It is intentionally transparent and can be revised after empirical validation.

### Quality-preview API

Added:

```text
POST /api/v1/inventory-events/quality
```

This parses and profiles a CSV/Excel transaction file without inserting inventory events. It returns the quality score, issue counts, summary and up to 100 detailed issues.

### Feature snapshots

Added:

- `backend/app/models/inventory_feature.py`
- `backend/app/services/feature_engineering_service.py`

The snapshot model stores:

- Current quantity
- Average, minimum and maximum quantity
- Daily and weekly sales
- Sales velocity
- Demand variability
- Sales value
- Inventory value
- Variance quantity and percentage
- Historical variance
- Adjustment frequency
- Count disagreement indicator
- Days of inventory
- ABC classification
- Lookback period
- Feature-set version
- Feature date

### Leakage-safe feature engineering

The feature service accepts an `as_of_date` and filters events so that only events at or before that date are used. Future transactions are excluded.

Features are calculated using explicit lookback windows such as 7, 14, 30, 60 or 90 days. The default version is `v1` and can be changed when the feature definition changes.

Event direction is currently defined as:

```text
SALE, WASTE, DAMAGE       negative movement
PURCHASE, RECEIPT, RETURN positive movement
OPENING_BALANCE           positive movement
Other event types         no stock movement by default
```

The movement rules must be reviewed when real Sage Evolution transaction semantics are confirmed.

### ABC classification

ABC classification is based on sales value contribution within the generated feature set:

- A: highest cumulative value contribution
- B: intermediate contribution
- C: lower contribution

The classification is stored with the feature snapshot rather than recalculated only in the user interface.

## Database migration

The current Alembic head after Phase 2 is revision `006`.

Apply migrations with:

```powershell
cd backend
$env:DEBUG='True'
python -m alembic upgrade head
```

The migration has not been applied automatically to the live database.

## Verification

The Phase 2 test suite includes:

- Data-quality issue detection
- Duplicate detection
- Quality-score persistence
- Feature generation
- As-of-date protection against future events
- Sales-value-based ABC classification

Verification result:

```text
18 passed
```

Python compilation also passes.

Existing non-blocking warnings remain for Pydantic schema configuration, SQLAlchemy's legacy `declarative_base` import and product response decimal serialisation.

## Research limitations recorded at this phase

1. Current quantity is derived from the signed event history. A reliable opening balance or stock ledger is required for operationally accurate on-hand quantities.
2. Adjustment events currently have non-negative quantities and no explicit direction. They are used as a variance proxy until adjustment semantics are extended.
3. Transfer events are not assigned a movement direction because source and destination locations are not yet represented on the event model.
4. Count disagreement requires linked first-count and second-count observations and is currently represented as an indicator based on count-event frequency.
5. ABC thresholds should be validated against the institutional procurement and financial policies.
6. The quality score is a transparent baseline, not a learned data-quality model.

These limitations are deliberately documented rather than hidden because they affect later AI interpretation and dissertation validity.

## Next phase

Phase 3 should implement and compare:

1. Rule-based anomaly detection
2. Statistical anomaly detection
3. Isolation Forest
4. Persisted anomaly scores
5. Evidence and feature-contribution explanations
6. Reproducible evaluation metrics
