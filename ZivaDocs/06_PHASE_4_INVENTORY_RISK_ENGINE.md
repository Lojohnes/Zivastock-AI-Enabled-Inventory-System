# Phase 4 — Explainable Inventory Risk Engine

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 4 combines anomaly results, stock-accuracy indicators, financial exposure, inventory cover, adjustment behaviour and ABC classification into a transparent inventory risk score.

The objective is prioritisation, not autonomous inventory modification.

```text
Anomaly evidence
    + Variance exposure
    + Financial exposure
    + Stockout exposure
    + Adjustment frequency
    + Historical accuracy
    ↓
Inventory Risk Score
    ↓
Risk level and priority
    ↓
AI Inventory Command Centre data
```

## Implemented components

### Risk persistence

Added:

- `backend/app/models/risk.py`
- Alembic revision `008_inventory_risk_scores.py`
- `database/migrations/V016__inventory_risk_scores.sql`

The `inventory_risk_scores` table stores each component score separately, together with:

- Total score
- Risk level
- ABC class
- Priority
- Explanation
- Calculation version
- Calculation date

### Risk-scoring service

Added:

- `backend/app/services/risk_scoring_service.py`

The current transparent weights are:

```text
Anomaly severity       25%
Variance magnitude     20%
Financial value        15%
Stockout exposure      20%
Adjustment frequency   10%
Historical accuracy    10%
```

The weights are implemented as a versioned service configuration and should be calibrated through later experiments.

### Component calculations

#### Anomaly component

Uses the anomaly score produced by the Phase 3 detectors.

#### Variance component

Normalises variance percentage against a 20% reference range.

#### Financial-value component

Ranks inventory value within the supplied product set and converts the percentile to a 0–100 score.

#### Stockout component

Uses days of inventory:

```text
0 days cover  = highest stockout exposure
14+ days cover = lowest stockout exposure
```

#### Adjustment component

Uses adjustment frequency against a five-adjustment reference range.

#### Historical-accuracy component

Combines variance percentage and the count-disagreement indicator.

### Risk levels

```text
0–44    LOW
45–69   MEDIUM
70–84   HIGH
85–100  CRITICAL
```

### Priority rules

ABC classification changes prioritisation but does not silently change the underlying score:

```text
CRITICAL risk                IMMEDIATE
ABC-A + HIGH                 IMMEDIATE
HIGH risk                    HIGH_PRIORITY
ABC-A/B + MEDIUM            HIGH_PRIORITY
MEDIUM risk                  REVIEW
LOW risk                     MONITOR
```

Every risk record contains component explanations such as:

```text
Anomaly contributed 95.0/100 to the component score
Stockout Exposure contributed 92.9/100 to the component score
Financial Exposure contributed 100.0/100 to the component score
Product is classified as ABC-A
```

## Command Centre response

The service returns an executive summary containing:

- Total products
- Critical risks
- High risks
- Anomalies requiring investigation
- Stockout risks
- ABC breakdown
- Top prioritised products

The top-priority records include:

- Product ID
- Location ID
- Feature date
- Total risk score
- Risk level
- ABC class
- Priority
- Explanation

This response is the initial backend data contract for the future AI Inventory Command Centre frontend.

## API endpoints

Added:

```text
POST /api/v1/risk/scores
POST /api/v1/risk/command-centre
```

The endpoint accepts feature rows and optional anomaly results. It can return calculated scores without persistence or persist the results when requested.

## Migration

The current Alembic head is:

```text
008 (head)
```

Apply deliberately with:

```powershell
cd backend
$env:DEBUG='True'
python -m alembic upgrade head
```

The migration has not been automatically applied to the live database.

## Verification

Phase 4 tests cover:

- Component-based score calculation
- Anomaly integration
- ABC-aware prioritisation
- Command Centre summary generation
- Risk-score persistence

Verification result:

```text
24 passed
```

Python compilation passed and the risk API routes were found in the generated OpenAPI document.

Existing non-blocking warnings remain for Pydantic schema configuration, SQLAlchemy's legacy `declarative_base` import and product response decimal serialisation.

## Research limitations

1. Weight values are an initial transparent configuration and require empirical calibration.
2. Financial-value ranking is relative to the supplied dataset and may need institution-specific thresholds.
3. Stockout exposure currently uses days of inventory; forecast uncertainty is not yet integrated.
4. Historical accuracy is still constrained by the current event and count representation.
5. Risk scores prioritise investigation but do not create autonomous inventory adjustments.
6. Recommendation acceptance and actual outcomes are not yet captured.

## Next phase

Phase 5 should implement demand forecasting and stockout/overstock prediction, then feed forecast outputs into the risk engine and scenario-analysis workflow.
