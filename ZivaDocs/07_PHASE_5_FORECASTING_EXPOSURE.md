# Phase 5 — Demand Forecasting, Stockout and Overstock Exposure

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 5 extends the intelligence pipeline from anomaly and risk scoring into predictive demand and inventory exposure analysis.

```text
Historical sales
    ↓
Forecast model comparison
    ↓
Selected demand forecast
    ↓
Stockout exposure
    ↓
Overstock and slow-moving exposure
    ↓
What-if scenario analysis
```

## Implemented forecasting models

Added:

- `backend/app/services/forecasting_service.py`

The implementation compares three transparent baselines:

1. **Naive:** next demand equals the latest observed demand.
2. **Moving average:** next demand equals the recent rolling average.
3. **Exponential smoothing:** next demand uses a pandas exponentially weighted mean.

These models are deliberately suitable for an initial research prototype. More complex models should only be added after the baselines are measured.

## Forecast evaluation

The service evaluates models using a time-ordered holdout period and calculates:

- MAE
- RMSE
- WAPE
- Validation record count

The selected model is the model with the lowest available WAPE, followed by MAE. No future observations are used in the training portion of the holdout evaluation.

Forecast records include:

- Product
- Location
- Selected model
- Forecast date
- Forecast horizon
- Predicted demand
- Lower bound
- Upper bound
- Evaluation metrics

The uncertainty bounds are based on historical residual variation and are not presented as artificial confidence values.

## Forecast persistence

Added:

- `backend/app/models/forecast.py`
- Alembic revision `009_forecasting_exposure.py`
- `database/migrations/V017__forecasting_exposure.sql`

New tables:

```text
forecast_results
inventory_exposures
```

## Stockout exposure

Stockout calculations use:

```text
Available stock = current quantity - safety stock
Days until stockout = available stock / predicted daily demand
```

Risk levels:

```text
0–2 days    CRITICAL
3–5 days    HIGH
6–10 days   MEDIUM
11+ days    LOW
No demand   LOW stockout risk, but may indicate non-moving inventory
```

The service calculates:

- Current quantity
- Predicted daily demand
- Safety stock
- Days until stockout
- Estimated stockout date
- Stockout risk level
- Explanation

## Overstock and slow-moving detection

The service identifies:

- Excess quantity above the target-days policy
- Slow-moving stock where inventory cover exceeds the configured threshold
- Non-moving stock where predicted demand is zero

Default values:

```text
Target inventory cover: 14 days
Slow-moving threshold: 30 days
```

These are configuration defaults and must be validated against institutional procurement policy.

## Scenario analysis

The forecasting service supports what-if scenarios using:

- Demand increase or decrease percentage
- Supplier delay days
- Safety stock
- Current stock
- Forecast demand
- Scenario horizon

Example scenarios:

```text
Normal demand
Demand +10%
Demand +20%
Supplier delay of 2 days
Supplier delay of 5 days
```

The response includes:

- Adjusted daily demand
- Demand change percentage
- Supplier delay
- Safety stock
- Days until stockout
- Ending quantity after the horizon
- Stockout risk

The scenario result is a deterministic calculation, not a fabricated probability.

## API endpoints

Added:

```text
POST /api/v1/forecast/compare
POST /api/v1/forecast/run
POST /api/v1/forecast/exposure
POST /api/v1/forecast/scenario
```

The endpoints support authenticated access and optional persistence for forecast and exposure results.

## Migration

The current Alembic head is:

```text
009 (head)
```

Apply deliberately with:

```powershell
cd backend
$env:DEBUG='True'
python -m alembic upgrade head
```

The migration has not been automatically applied to the live database.

## Verification

Phase 5 tests cover:

- Comparison of all three forecasting baselines
- Non-negative forecasts
- Reproducible forecast generation
- Stockout risk calculation
- Overstock detection
- Non-moving detection
- Demand-change scenarios
- Supplier-delay scenarios
- Forecast persistence
- Exposure persistence

Verification result:

```text
28 passed
```

Python compilation passed and all four forecast API routes were found in the generated OpenAPI document.

Existing non-blocking warnings remain for Pydantic schema configuration, SQLAlchemy's legacy `declarative_base` import and product response decimal serialisation.

## Research limitations

1. The initial models are baseline forecasting approaches, not evidence that one model is universally superior.
2. Forecast uncertainty is estimated from historical residual variation.
3. Stockout exposure depends on the quality of current inventory and event history.
4. Supplier lead times are currently scenario inputs rather than learned supplier-specific values.
5. Overstock thresholds require institutional policy validation.
6. Forecast outputs are not yet connected to prescriptive recommendations or human approval.

## Next phase

Phase 6 should connect anomaly, risk and forecast outputs to:

- Explainable replenishment recommendations
- Targeted recount recommendations
- Investigation recommendations
- Transfer and procurement recommendations
- Human approval, rejection and override
- Recommendation outcomes and feedback
