# Experiment Protocol

## Protocol identity

**Protocol:** ZivaStock Inventory Intelligence Validation  
**Default dataset:** Simulated POS/ERP transaction data  
**Default seed:** 42  
**Default scenario:** `abnormal_adjustment`  
**Default duration:** 60 days  
**As-of date:** 2026-03-01 for the default run

## Dataset protocol

1. Generate transactions with `run_demo_pipeline.py`.
2. Record scenario, seed, date range and product catalogue.
3. Preserve raw transaction CSV.
4. Hash each output artifact.
5. Do not mix simulated and institutional records without explicit dataset labels.

## Anomaly protocol

Compare:

1. Rule-based detector
2. Statistical Z-score detector
3. Isolation Forest

Record:

- Feature-set version
- Thresholds
- Contamination configuration
- Random state
- Dataset version
- Anomaly rate
- Precision, recall and F1 when confirmed labels exist
- False positives and false negatives

Simulator-injected anomalies may be used for controlled pipeline verification but must be distinguished from naturally confirmed anomalies.

## Forecast protocol

1. Sort sales observations by event date.
2. Use a time-ordered holdout period.
3. Compare naive, moving average and exponential smoothing.
4. Select by WAPE, then MAE.
5. Record MAE, RMSE and WAPE.
6. Record lower and upper uncertainty bounds.
7. Do not use future observations in feature or training construction.

## Risk protocol

Record:

- Component weights
- Anomaly input
- Variance input
- Financial exposure input
- Stockout exposure input
- Adjustment input
- Accuracy input
- ABC classification
- Calculation version

Risk weights must be treated as experimental configuration, not universal truth.

## Recommendation protocol

Record:

- Recommendation type
- Evidence list
- Evidence coverage score
- Expected impact
- Human decision
- Decision reason
- Override flag
- Actual outcome
- Variance after action
- Stockout avoidance outcome

## User evaluation protocol

Participants should evaluate:

- Usability
- Perceived usefulness
- Explainability
- Trust
- Decision confidence
- Recommendation clarity
- Willingness to use

Use a documented questionnaire and retain anonymised responses.

## Baseline comparison

Compare:

```text
Manual/legacy process
Current ZivaStock digital process
AI-enabled ZivaStock process
```

Measure:

- Stocktake time
- Reconciliation time
- Reporting time
- Decision time
- Inventory accuracy
- Anomaly identification
- Stockout prioritisation
- Recommendation usefulness

## Reproducibility record

Every experiment must record:

```text
Dataset and hash
Dataset version
Feature-set version
Algorithm
Hyperparameters
Training period
Testing period
Random seed
Metrics
Model version
Execution date
```

## Ethical protocol

- Minimise personal data.
- Anonymise institutional records where required.
- Do not infer theft from anomalies.
- Treat AI results as decision support.
- Record human reasoning for overrides.
- Separate operational monitoring from inappropriate employee surveillance.
