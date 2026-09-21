# ZivaStock Dissertation Architecture Assessment

**Project:** ZivaStock → AI-Enabled Inventory Intelligence Framework  
**Proposed dissertation title:** Development and Validation of an Explainable AI-Enabled Inventory Intelligence Framework for Stock Accuracy, Anomaly Detection and Predictive Decision Support in Institutional Retail Environments  
**Assessment status:** Initial repository audit completed  
**Implementation status:** No AI implementation changes made at the time of this assessment

---

## 1. Research Problem and Intended Transformation

The University Business Unit operates in an FMCG retail environment where Sage Evolution and related operational processes require substantial manual work. The problem is not only the recording of physical stock counts. The larger problem is converting fragmented operational data and physical stocktake results into accurate, explainable and timely management decisions.

ZivaStock should therefore be extended into an **AI-enabled inventory intelligence and decision-support platform**, while preserving its existing stocktake, reconciliation, offline mobile and governance capabilities.

The intended transformation is:

```text
Current ZivaStock:
Stocktake → Count → Reconciliation → Adjustment → Report

Target platform:
Operational data
    → Data quality
    → Inventory events
    → Feature engineering
    → Anomaly detection
    → Risk scoring
    → Demand forecasting
    → Stockout/overstock prediction
    → Explainability
    → Recommendation
    → Human decision
    → Outcome and feedback
```

The system should support four levels of intelligence:

1. **Descriptive:** What is happening to inventory?
2. **Diagnostic:** Why is it happening?
3. **Predictive:** What is likely to happen next?
4. **Prescriptive:** What should management consider doing?

---

## 2. Existing-System Architecture Assessment

### 2.1 Current architecture

```text
Android Mobile App
    Kotlin, Room, barcode scanning, WorkManager sync
          │
          ▼
FastAPI Backend
    REST API, business services, JWT, RBAC, audit middleware
          │
          ▼
PostgreSQL Database
    Products, locations, stocktakes, counts, adjustments,
    imports, sync queues, audit trail and reports
          │
          ▼
React Web Dashboard
    React, TypeScript, Material UI, Redux Toolkit and reports
```

### 2.2 Backend

The backend uses FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, JWT authentication, RBAC, rate limiting, audit logging, import processing and report/export services.

API groups currently include:

- Authentication
- Users and roles
- Products and categories
- Counts
- Stocktake sessions
- Adjustments
- Synchronisation
- Reports
- Locations
- Imports
- Exports

The canonical application entry point is `backend/main.py`. API routes are registered under `/api/v1` in `backend/app/api/v1/__init__.py`.

### 2.3 Stocktake workflow

ZivaStock already supports:

```text
Create session
    → Assign users/sections
    → Start stocktake
    → First count
    → Second count
    → Compare counts
    → Reconcile discrepancies
    → Generate adjustment
    → Approve/reject adjustment
    → Post adjustment
    → Complete/archive session
```

The system has separate first-count and second-count entities, count uniqueness rules, validation, segregation-of-duties enforcement and adjustment approval controls.

### 2.4 Database

Current operational entities include:

- Users
- Roles
- Permissions
- Product categories
- Products
- Locations
- Shelves
- Shelf sections
- Stocktake sessions
- Session assignments
- First counts
- Second counts
- Duplicates
- Adjustments
- Import batches
- Sync queues
- Audit trail
- Reports
- Exports

The database migration history includes schema, audit, synchronisation, reporting, import/export, indexes, views, stored procedures, triggers and partitioning.

### 2.5 Mobile and offline capability

The Android application provides:

- Kotlin implementation
- Room local persistence
- Barcode scanning with CameraX and ML Kit
- Offline count capture
- WorkManager background synchronisation
- Retrofit API communication
- Hilt dependency injection
- Synchronisation monitoring

The backend synchronisation process supports client identifiers, idempotent writes, retry handling, push and pull operations.

### 2.6 Frontend

The frontend uses React 18, TypeScript, Vite, Redux Toolkit, Material UI, MUI Data Grid, Recharts and Axios.

Current operational pages include:

- Dashboard
- Stocktake
- Products
- Imports
- Reports
- Counts
- Users
- Roles
- Settings
- Profile

The dashboard currently provides operational KPIs such as sessions, products, counts, duplicates, section completion and active users. It does not yet provide AI risk, anomaly, forecasting or recommendation intelligence.

---

## 3. Existing-System Strengths

ZivaStock already provides a strong implementation foundation:

1. Real-world stocktake workflow
2. Physical counting through mobile devices
3. First-count and second-count controls
4. Reconciliation and adjustment workflow
5. Approval and posting controls
6. Product and location structures
7. Import and export mechanisms
8. Offline-first mobile operation
9. Synchronisation queue and retry handling
10. JWT authentication
11. Role-based access control
12. Audit trail
13. PostgreSQL persistence
14. Reporting functionality
15. Docker deployment configuration
16. Existing technical documentation

The dissertation contribution should therefore focus on the intelligence layer rather than replacing the operational platform.

---

## 4. Gap Analysis

| Dissertation requirement | Current status | Required extension |
|---|---|---|
| Unified inventory-event model | Not implemented | Add sales, purchases, returns, transfers, counts, waste and adjustment events |
| POS/ERP/Sage integration | Limited import functionality | Add configurable transaction import and simulator |
| Data-quality pipeline | Basic import error logging | Add duplicate, missing, invalid, orphan and consistency checks |
| Feature-engineering pipeline | Not implemented | Add reusable inventory, sales and accuracy features |
| Rule-based anomaly detection | Not implemented as a module | Add transparent baseline |
| Statistical anomaly detection | Not implemented | Add Z-score or robust statistical baseline |
| Machine-learning anomaly detection | Not implemented | Add Isolation Forest initially |
| Demand forecasting | Not implemented | Add moving average and exponential smoothing baselines |
| Stockout prediction | Not implemented | Add transparent stock-cover and demand-based calculation |
| Overstock detection | Not implemented | Add slow-moving and excess-stock analysis |
| ABC analysis | Not implemented | Add value-based classification |
| Inventory risk scoring | Not implemented | Add documented weighted risk engine |
| Explainable AI | Not implemented | Store evidence, contributions and explanations |
| Decision recommendations | Not implemented | Add recommendation engine |
| Human approval and override | Partially exists for adjustments | Extend to AI recommendations |
| Model registry | Not implemented | Store model, dataset, feature and metric versions |
| AI Model Laboratory | Not implemented | Add experiment and comparison interface |
| Scenario simulation | Not implemented | Add demand, supply-delay and stock-reduction scenarios |
| Feedback and outcome tracking | Not implemented | Capture approval, rejection, override and outcome |
| AI dashboard | Operational dashboard only | Add AI Inventory Command Centre |
| AI Copilot | Not implemented | Optional final-stage feature using actual analytics outputs |

---

## 5. Proposed Target Architecture

The target architecture should remain a modular extension of the existing FastAPI application initially. A microservice architecture is not necessary for the dissertation prototype.

```text
Presentation Layer
    React AI Inventory Command Centre
    Existing operational pages
    AI Model Laboratory
    Optional AI Copilot
          │
          ▼
Application/API Layer
    Authentication, RBAC and operational APIs
    Inventory intelligence APIs
    Experiment APIs
    Recommendation approval APIs
          │
          ▼
Domain Services
    Inventory events
    Data quality
    Feature engineering
    Anomaly detection
    Forecasting
    Risk scoring
    Stockout/overstock analysis
    Explainability
    Recommendations
    Feedback
          │
          ▼
Data and ML Layer
    PostgreSQL operational data
    Feature snapshots
    Experiment results
    Model registry
    Model artifacts
    Imported and simulated transactions
          │
          ▼
Data Sources
    Sage Evolution exports
    POS exports
    Stocktake counts
    Product catalogue
    Adjustments
    Returns, transfers, waste and damage
    Transaction simulator
    Android offline synchronisation
```

The first implementation should use services within the existing backend. A worker process may be added later for large imports or model training.

---

## 6. Proposed Database Extensions

### 6.1 Inventory events

```text
inventory_events
-----------------
id
 event_uuid
product_id
location_id
event_type
quantity
unit_cost
transaction_value
event_timestamp
user_id
source_system
source_record_id
reference_number
stocktake_session_id
import_batch_id
created_at
```

Supported event types:

```text
SALE, PURCHASE, RECEIPT, RETURN, TRANSFER, STOCKTAKE,
COUNT, ADJUSTMENT, WASTE, DAMAGE, PRICE_CHANGE,
LOCATION_CHANGE, OPENING_BALANCE, CLOSING_BALANCE
```

Source record identifiers should support deduplication. Event timestamps must be separate from ingestion timestamps. Imported records must retain their source system.

### 6.2 Data quality

```text
data_quality_batches
--------------------
id
import_batch_id
dataset_type
quality_score
total_records
valid_records
invalid_records
duplicate_records
missing_value_count
created_at
completed_at
```

```text
data_quality_issues
--------------------
id
batch_id
record_reference
issue_type
field_name
severity
description
raw_value
resolved
resolution_note
```

### 6.3 Feature snapshots

```text
inventory_features
-------------------
id
product_id
location_id
feature_date
current_quantity
average_quantity
minimum_quantity
maximum_quantity
daily_sales
weekly_sales
sales_velocity
demand_variability
inventory_value
variance_quantity
variance_percentage
historical_variance
adjustment_frequency
count_disagreement
days_of_inventory
abc_class
feature_version
created_at
```

### 6.4 Anomaly results

```text
anomaly_results
---------------
id
product_id
location_id
feature_date
model_version_id
algorithm
anomaly_flag
anomaly_score
risk_level
threshold_used
evidence
feature_contributions
created_at
```

### 6.5 Forecast results

```text
forecast_results
-----------------
id
product_id
location_id
model_version_id
forecast_date
horizon_days
predicted_demand
lower_bound
upper_bound
actual_demand
created_at
```

### 6.6 Risk scores

```text
inventory_risk_scores
----------------------
id
product_id
location_id
calculation_date
anomaly_score
variance_score
financial_value_score
stockout_score
adjustment_score
accuracy_score
criticality_score
total_score
risk_level
calculation_version
created_at
```

### 6.7 Recommendations and decisions

```text
ai_recommendations
-------------------
id
product_id
location_id
recommendation_type
recommendation_text
priority
confidence_or_uncertainty
evidence
expected_impact
model_version_id
status
created_at
expires_at
```

```text
recommendation_decisions
-------------------------
id
recommendation_id
decision
decided_by
decision_reason
override_flag
decided_at
```

```text
recommendation_outcomes
------------------------
id
recommendation_id
actual_action
outcome_status
actual_result
variance_after_action
stockout_avoided
recorded_by
recorded_at
```

### 6.8 Model registry and experiments

```text
model_versions
--------------
id
model_name
algorithm
version
dataset_version
feature_set_version
hyperparameters
training_start
training_end
evaluation_metrics
artifact_path
status
created_by
created_at
```

```text
experiments
-----------
id
experiment_name
dataset_version
model_version_id
baseline_model
test_period
random_seed
metrics
confusion_matrix
notes
created_by
created_at
```

---

## 7. AI and Data Pipeline Design

### 7.1 Ingestion pipeline

```text
Upload
  → Schema detection
  → Column mapping
  → Validation
  → Product/location resolution
  → Duplicate detection
  → Data-quality report
  → Accepted records
  → Inventory event creation
```

Initial inputs should include Sage Evolution exports, POS files, product data, stocktake results, adjustments, returns, transfers, waste/damage records and generated simulator data.

### 7.2 Feature engineering

Use documented time windows such as 7, 14, 30, 60 and 90 days. Initial features should include current inventory, sales velocity, rolling demand, demand variability, inventory value, days of inventory, reorder level, count variance, adjustment frequency, returns, waste/damage and ABC classification.

Historical features must be generated without using future information. This is essential to prevent data leakage.

### 7.3 Anomaly detection experiment

Start with:

1. Rule-based threshold baseline
2. Statistical Z-score or robust statistical baseline
3. Isolation Forest as the initial machine-learning model

Isolation Forest is a suitable first model because it supports unsupervised detection, multiple features and a relatively interpretable implementation. Other models should only be added if the available data and research questions justify them.

### 7.4 Demand forecasting

Use a staged comparison:

1. Naive previous-period baseline
2. Moving average
3. Exponential smoothing
4. Seasonal model if sufficient history exists
5. More complex models only when they produce meaningful improvement

Evaluate using MAE, RMSE and WAPE. MAPE should be used carefully where zero-demand periods exist.

### 7.5 Stockout prediction

The initial transparent calculation can be:

```text
Expected days until stockout = available stock / predicted average daily demand
```

A safety-stock version can be added:

```text
Usable stock = current stock - safety stock
Expected days until stockout = usable stock / predicted daily demand
```

The interface should show current stock, predicted demand, safety stock, estimated stockout date and forecast uncertainty.

### 7.6 Risk scoring

Use a transparent weighted model rather than an unexplained black box. An initial configuration could be:

```text
25% anomaly severity
20% variance magnitude
20% stockout exposure
15% financial value
10% adjustment frequency
10% historical stock accuracy
```

The weights must be configurable and evaluated experimentally.

### 7.7 Explainability

Every alert should distinguish:

```text
Model result
Evidence
Recommendation
Human decision
Actual outcome
```

An anomaly must not be treated as proof of theft or misconduct. The system should use wording such as:

> Anomalous inventory behaviour detected. Investigation recommended.

---

## 8. Research-to-System Mapping

### Research aim

To develop and validate an explainable AI-enabled inventory intelligence framework that improves stock accuracy analysis, anomaly detection and predictive decision support in an institutional retail environment.

### Possible research questions

1. How can stocktake, transactional and inventory-movement data be integrated into a unified inventory intelligence framework?
2. To what extent does machine-learning anomaly detection improve inventory anomaly identification compared with manual or threshold-based approaches?
3. How accurately can demand forecasting and stockout prediction support inventory planning in an institutional retail environment?
4. How does explainable AI affect managers' understanding, trust and acceptance of inventory recommendations?
5. To what extent does human-in-the-loop AI decision support improve inventory-management efficiency and decision quality?

### Possible hypotheses

- **H1:** AI-enabled anomaly detection achieves a higher F1-score than threshold-based anomaly detection.
- **H2:** The AI-enabled framework reduces the time required to identify and prioritise inventory problems.
- **H3:** Explainable recommendations produce higher perceived trust and usefulness than unexplained alerts.
- **H4:** Forecast-informed decision support improves stockout-risk identification compared with current manual practice.

These should be refined after literature review and supervisor review.

### Variables

Independent variables:

- Inventory-management approach
- Detection method
- Explainability condition
- Forecasting method
- Availability of AI recommendations

Dependent variables:

- Inventory accuracy
- Precision, recall and F1-score
- Forecasting MAE/RMSE/WAPE
- Stockout prediction accuracy
- Decision time
- Recommendation acceptance
- User trust
- Perceived usefulness
- Usability

Control variables:

- Product category
- Product value
- Demand volume
- Location
- Time period
- Dataset type
- Stocktake session type

---

## 9. Validation Strategy

Compare three conditions:

```text
A. Existing manual process
B. Current ZivaStock digital stocktake
C. AI-enabled ZivaStock inventory intelligence platform
```

### Operational measures

- Stocktake duration
- Reconciliation duration
- Reporting time
- Manual steps
- Issues prioritised
- Manager decision time

### Accuracy measures

- Absolute variance
- Variance percentage
- Inventory record accuracy
- Recount confirmation rate
- Adjustment accuracy

### Anomaly-model measures

- Precision
- Recall
- F1-score
- False-positive rate
- False-negative rate
- ROC-AUC where labelled data permits

### Forecast measures

- MAE
- RMSE
- WAPE
- MAPE where valid
- Forecast interval coverage

### Human evaluation

- Perceived usefulness
- Explainability
- Trust
- Decision confidence
- Usability
- Recommendation acceptance
- Override frequency

No performance claims should be made until experiments have actually been executed.

---

## 10. Development Roadmap

### Phase 0 — Baseline stabilisation

- Correct backend test import issues
- Confirm the canonical backend entry point
- Establish repeatable local setup
- Confirm database migration process
- Document Redis and environment dependencies
- Document Android v1/v2 status
- Capture baseline operational measurements

### Phase 1 — Inventory event and import layer

- Add inventory events
- Add transaction import
- Add Sage-compatible mapping
- Add product-code mapping
- Add duplicate detection
- Add source-system tracking
- Add import preview and validation

### Phase 2 — Data quality and features

- Add data-quality scoring
- Store quality issues
- Add feature-generation services
- Add feature snapshots
- Add dataset versioning
- Add leakage-safe time splits

### Phase 3 — Anomaly detection

- Rule baseline
- Statistical baseline
- Isolation Forest
- Anomaly persistence
- Evidence generation
- Model comparison metrics

### Phase 4 — Risk and ABC analysis

- ABC classification
- Risk scoring
- Product prioritisation
- Financial exposure
- Historical accuracy indicators

### Phase 5 — Forecasting and stockout prediction

- Moving-average baseline
- Exponential smoothing
- Model evaluation
- Demand forecasts
- Stockout calculations
- Overstock and slow-moving detection

### Phase 6 — Decision support

- Replenishment recommendation
- Targeted recount recommendation
- Investigation recommendation
- Transfer recommendation
- Monitoring recommendation
- Approval, rejection and override workflow
- Outcome capture

### Phase 7 — AI Inventory Command Centre

- Inventory accuracy
- Total inventory value
- Critical risks
- Anomalies requiring investigation
- Stockout risks
- Overstock alerts
- Slow-moving products
- Pending recommendations
- Risk matrix
- Forecast charts
- Product intelligence view

### Phase 8 — Simulator and scenarios

- Normal operations
- High demand
- Unusual adjustment
- Stock discrepancy
- Supplier delay
- Demand increase/decrease
- Transfer scenario

### Phase 9 — AI Model Laboratory

- Dataset selection
- Feature-set selection
- Model selection
- Training and evaluation
- Model comparison
- Feature importance
- Error analysis
- Model version registration

### Phase 10 — Validation and dissertation evidence

- Baseline comparison
- Anomaly model comparison
- Forecasting comparison
- Stockout evaluation
- Usability evaluation
- Explainability/trust evaluation
- Operational-efficiency evaluation
- Repeatable demonstration

---

## 11. Risks and Dependencies

### Real data access

Access to Sage Evolution, POS and historical stocktake data is the most important dependency. Begin with simulated data and anonymised exports where necessary.

### Limited labelled anomalies

Use unsupervised methods, controlled anomaly injection and confirmed recount outcomes. Label limitations must be reported honestly.

### Historical data quality

Build data quality before model training. Preserve rejected records and reasons, version cleaned datasets and include quality scores in experiments.

### Data leakage

Use time-based training/testing splits. Features must contain only information available at the prediction time.

### Scope expansion

Prioritise the research spine:

```text
Events → Data quality → Features → Anomalies → Risk → Forecasting
→ Explainability → Recommendations → Validation
```

The AI Copilot, advanced deep learning and full live Sage integration should remain secondary unless time and data availability support them.

### Ethics

An anomaly is not proof of theft or employee misconduct. AI outputs must support investigation and management review, not automate accusations.

### Existing technical issues

The repository inspection identified backend test import-path failures, optional Redis availability, Android v1/v2 duplication, Android TODOs and limited manual browser verification. These should be addressed or documented during Phase 0.

---

## 12. Recommended Dissertation Contribution

The strongest defensible contribution is not simply “using AI in inventory.” A more precise contribution is:

> A validated, explainable and human-governed inventory intelligence framework that combines physical stocktake accuracy, transactional inventory events, anomaly detection, demand forecasting and prescriptive decision support for institutional FMCG retail environments.

The project should distinguish between:

- Established approaches
- Adapted approaches
- Proposed framework contribution
- Empirically validated contribution

Novelty claims should only be made after completing the literature review.

---

## 13. Immediate Next Step

The implementation sequence should be:

1. Stabilise and test the existing system
2. Add the inventory-event model
3. Add transaction import and simulator
4. Add data-quality scoring
5. Add reproducible feature engineering
6. Implement rule/statistical/Isolation Forest comparison
7. Add risk scoring and explainability
8. Add forecasting and stockout prediction
9. Add human-governed recommendations
10. Build the AI Inventory Command Centre
11. Run reproducible validation experiments
12. Produce dissertation documentation

ZivaStock is a suitable foundation. The main work is to add a properly designed intelligence and research layer without damaging the stocktake and control workflows already present.
