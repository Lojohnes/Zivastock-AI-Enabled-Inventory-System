# Phase 3 — Explainable Anomaly Detection

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 3 introduces genuine anomaly-detection functionality on top of the Phase 2 feature snapshots. It deliberately compares transparent baselines with a machine-learning model rather than presenting a chatbot or hard-coded alert as AI.

Implemented algorithms:

1. Rule-based threshold detection
2. Statistical Z-score detection
3. Isolation Forest

## Implemented components

### Dependency

Added scikit-learn to `backend/requirements.txt`.

The development environment was verified with scikit-learn installed. Isolation Forest is imported by the service when that algorithm is executed.

### Model registry

Added:

- `backend/app/models/ml.py`
- Alembic revision `007_anomaly_detection.py`
- `database/migrations/V015__anomaly_detection.sql`

The `model_versions` table records:

- Model name
- Algorithm
- Version
- Dataset version
- Feature-set version
- Features used
- Hyperparameters
- Training period
- Evaluation metrics
- Artifact path
- Status
- Creator
- Creation timestamp

### Anomaly results

The `anomaly_results` table records:

- Product
- Location
- Feature date
- Model version
- Algorithm
- Anomaly flag
- Anomaly score from 0 to 100
- Risk level
- Threshold used
- Evidence
- Feature contributions
- Creation timestamp

### Detection service

Added:

- `backend/app/services/anomaly_detection_service.py`

All three algorithms return a common result format containing:

```text
product_id
location_id
feature_date
algorithm
anomaly_flag
anomaly_score
risk_level
threshold_used
evidence
feature_contributions
```

## Algorithm details

### Rule-based baseline

The baseline combines transparent signals:

- Variance percentage
- Adjustment frequency
- Low days of inventory
- Count-disagreement indicator

The baseline produces a score and records the contributing factors. The default alert threshold is 50/100.

### Statistical baseline

The statistical detector calculates peer-distribution Z-scores across available numeric features. It flags a record when the maximum absolute Z-score reaches the configured threshold.

The default threshold is 2.5 standard deviations.

### Isolation Forest

Isolation Forest is implemented using scikit-learn with:

- 100 estimators
- Random state 42
- Configurable contamination
- Multiple inventory and demand features

The model uses its learned isolation signal for anomaly labels and converts decision-function values into a 0–100 comparative score. Feature contributions are estimated from standardized deviations weighted by model feature importance. These contributions are evidence for interpretation and are not claimed to be causal explanations.

Isolation Forest requires at least two feature records. The service raises a validation error instead of fabricating a prediction for an insufficient dataset.

## Explainability distinction

The system separates:

```text
Model output:
Anomaly flag and score

Evidence:
Observed feature deviations and operational signals

Recommendation:
Not implemented yet; will be added in the decision-support phase
```

An anomaly result does not imply theft, fraud or employee misconduct. It indicates that the record differs materially from its peer or configured operational expectations.

## Experiment comparison

The comparison service returns descriptive metrics for each algorithm:

- Record count
- Anomaly count
- Anomaly rate
- Mean anomaly score

When confirmed labels are supplied, it also calculates:

- Precision
- Recall
- F1-score

The system does not fabricate precision, recall or F1 values when labels are unavailable. Controlled simulator labels and confirmed recount outcomes should be used for the dissertation evaluation.

## API endpoints

Added:

```text
POST /api/v1/anomalies/detect
POST /api/v1/anomalies/compare
```

`/detect` accepts feature rows and one or more algorithms. It can either return results without persistence or persist model-version and anomaly-result records.

`/compare` runs all three detectors and returns comparison metrics. Optional labels enable supervised evaluation metrics.

## Migration

The current Alembic head is:

```text
007 (head)
```

Apply migrations deliberately with:

```powershell
cd backend
$env:DEBUG='True'
python -m alembic upgrade head
```

The migration has not been applied automatically to the live database.

## Verification

Phase 3 tests cover:

- Common output structure for all algorithms
- Anomaly-score range validation
- Rule-based evidence
- Statistical model comparison
- Isolation Forest execution
- Labelled precision/recall/F1 calculation
- Model-version and anomaly-result persistence

Verification result:

```text
21 passed
```

Python compilation passed and the anomaly API routes were found in the generated OpenAPI document.

Existing non-blocking warnings remain for Pydantic schema configuration, SQLAlchemy's legacy `declarative_base` import and product response decimal serialisation.

## Research limitations

1. Confirmed anomaly labels are not yet available for institutional data.
2. Simulator-injected anomalies should not be treated as equivalent to naturally occurring operational anomalies.
3. Isolation Forest feature contributions are interpretive evidence, not causal explanations.
4. Thresholds and risk-level boundaries require empirical calibration.
5. The current adjustment representation does not preserve movement direction.
6. Anomaly detection is not yet connected to a human approval/recommendation workflow.

## Next phase

Phase 4 should implement:

- Transparent inventory risk scoring
- ABC plus anomaly prioritisation
- Stockout exposure integration
- Product-level risk explanations
- Risk ranking API
- Initial AI Inventory Command Centre data contract
