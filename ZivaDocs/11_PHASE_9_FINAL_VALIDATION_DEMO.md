# Phase 9 — Final Integration, Validation Evidence and Demonstration

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 9 creates the repeatable final demonstration and validation evidence pipeline. It connects the implemented research modules in an offline, reproducible run:

```text
Simulated POS/ERP transactions
    ↓
Inventory features
    ↓
Isolation Forest anomaly detection
    ↓
Risk scoring
    ↓
Demand forecasting
    ↓
Stockout/overstock exposure
    ↓
Decision recommendations
    ↓
Validation artifacts
```

## Repeatable demonstration pipeline

Added:

- `backend/scripts/run_demo_pipeline.py`
- `backend/tests/test_demo_pipeline.py`

Run from the backend directory:

```powershell
python scripts\run_demo_pipeline.py `
  --days 60 `
  --seed 42 `
  --output ..\reports\demo_phase9
```

The demonstration uses:

```text
Scenario: abnormal_adjustment
Seed: 42
Default start date: 2026-01-01
```

All records are simulated and must not be described as institutional data.

## Generated artifacts

The pipeline writes:

```text
reports/demo_phase9/
├── transactions.csv
├── features.csv
├── anomaly_results.csv
├── forecast_comparison.csv
├── forecasts.csv
├── exposure.csv
├── risk_scores.csv
├── recommendations.csv
└── validation_evidence.json
```

The validation evidence file records:

- Scenario
- Seed
- Number of days
- As-of date
- Product count
- Transaction count
- Feature count
- Anomaly count
- High/critical risk count
- Stockout risk count
- Recommendation count
- Artifact paths
- Artifact record counts
- SHA-256 hashes
- Validation notes

This makes the demonstration dataset and derived results auditable and reproducible.

## Demonstration run verified

A 60-day run produced:

```text
Products: 5
Transactions: 352
Features: 5
Anomaly results: 5
High/critical risks: 1
Stockout risks: 5
Recommendations: 9
```

These are outputs from the local simulated run and are not research claims about institutional data or model performance.

## Final examiner demonstration

### Step 1 — Start the existing platform

Start the backend and frontend using the existing project setup.

### Step 2 — Generate the demonstration artifacts

```powershell
cd backend
python scripts\run_demo_pipeline.py --days 60 --seed 42 --output ..\reports\demo_phase9
```

### Step 3 — Load the prepared operational data

If the database has been migrated and the simulator data is being loaded operationally, use the transaction ingestion endpoint:

```text
POST /api/v1/inventory-events/ingest
```

Use:

```text
source_system = simulator
```

The demonstration artifacts can also be reviewed offline without loading the database.

### Step 4 — Open AI Inventory Command Centre

Navigate to:

```text
/command-centre
```

Demonstrate:

- Critical risks
- High risks
- Stockout exposure
- Excess inventory
- Pending recommendations
- Top product prioritisation

### Step 5 — Select the highest-risk product

The product detail dialog should show:

- Product identity
- Risk score
- ABC classification
- Anomaly explanation
- Stockout exposure
- Recommendation history

### Step 6 — Review a recommendation

Open a pending recommendation and demonstrate:

- Evidence
- Recommendation text
- Priority
- Evidence coverage
- Approve
- Reject
- Override with reason

### Step 7 — Open AI Model Laboratory

Navigate to:

```text
/model-laboratory
```

Demonstrate:

- Registered algorithms
- Model versions
- Evaluation metrics
- Recommendation outcome analytics
- Demand-change scenario
- Supplier-delay scenario
- Stock projection chart

### Step 8 — Explain research governance

Emphasise:

```text
AI detects.
AI explains.
AI recommends.
A human decides.
The outcome is recorded.
```

## Integration health check

Added:

```powershell
cd backend
python scripts\verify_phase9.py
```

The health check verifies:

- Required intelligence API routes
- Migration head file
- Demonstration runner
- Phase documentation presence

It does not claim that the production database has been migrated or populated.

## Validation evidence strategy

The final evidence set should contain:

### Technical evidence

- Backend test output
- Frontend build output
- API route verification
- Migration head
- Demonstration artifact hashes

### AI evidence

- Rule-based anomaly metrics
- Statistical anomaly metrics
- Isolation Forest metrics
- Forecast MAE/RMSE/WAPE
- Stockout exposure outputs
- Recommendation outcome rates

### Operational evidence

- Manual process baseline
- Current ZivaStock baseline
- AI-enabled workflow measurements
- Reconciliation time
- Decision time
- Report-generation time

### User evidence

- Usability survey
- Explainability rating
- Perceived usefulness
- Trust rating
- Decision confidence
- Recommendation acceptance and override reasons

Only values generated from completed experiments should be used in the dissertation.

## Verification

Phase 9 demonstration test:

```text
Passed
```

The 30-test backend suite remains passing. The frontend production build remains passing.

## Final project status

Implemented layers now include:

```text
1. Repository stabilisation
2. Inventory events and imports
3. Data quality and features
4. Anomaly detection
5. Risk scoring
6. Forecasting and exposure
7. Human decision support
8. AI Command Centre
9. AI Model Laboratory
10. Repeatable validation demonstration
```

## Remaining work before dissertation submission

1. Apply migrations in the controlled research environment.
2. Populate the database with the demonstration dataset.
3. Browser-test the Command Centre and Model Laboratory.
4. Run formal experiments with documented datasets and seeds.
5. Collect user evaluation responses.
6. Capture baseline operational measurements.
7. Export final validation evidence.
8. Write the dissertation results and discussion chapters.
