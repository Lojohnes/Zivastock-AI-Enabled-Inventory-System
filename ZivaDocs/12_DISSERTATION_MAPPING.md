# Dissertation-to-System Mapping

## Chapter 1 — Introduction

System evidence:

- Institutional FMCG inventory problem
- Manual Sage Evolution processes
- Existing ZivaStock operational baseline
- AI-enabled inventory intelligence motivation

Relevant documents:

- `01_ARCHITECTURE_ASSESSMENT.md`
- `02_PHASE_0_BASELINE.md`

## Chapter 2 — Literature Review

The implementation provides research subjects for the literature review:

- Inventory accuracy
- Physical stocktaking
- Data quality
- Anomaly detection
- Explainable AI
- Demand forecasting
- Stockout and overstock prediction
- ABC inventory analysis
- Human-in-the-loop decision support
- Trust and usability

The system must distinguish established techniques from the proposed institutional-retail framework.

## Chapter 3 — Research Methodology

System support:

- Reproducible transaction simulator
- Fixed random seed
- Versioned feature set
- Model registry
- Time-ordered forecast validation
- Rule, statistical and Isolation Forest comparison
- Recommendation outcome tracking
- User decision and override capture
- Validation evidence package

Relevant documents:

- `03_PHASE_1_INVENTORY_EVENTS.md`
- `04_PHASE_2_DATA_QUALITY_FEATURES.md`
- `05_PHASE_3_ANOMALY_DETECTION.md`
- `07_PHASE_5_FORECASTING_EXPOSURE.md`
- `11_PHASE_9_FINAL_VALIDATION_DEMO.md`

## Chapter 4 — System Analysis and Design

System evidence:

- Existing ZivaStock audit
- Target architecture
- Unified inventory-event model
- Data-quality layer
- Feature-engineering layer
- Human-governed recommendation workflow
- Offline-first preservation

Relevant document:

- `01_ARCHITECTURE_ASSESSMENT.md`

## Chapter 5 — Implementation

Implementation areas:

- FastAPI backend
- PostgreSQL/Alembic migrations
- React management interface
- Inventory-event ingestion
- Simulator
- Data-quality service
- Feature engineering
- Anomaly detection
- Risk scoring
- Forecasting
- Exposure analysis
- Recommendations
- Command Centre
- Model Laboratory

## Chapter 6 — Results and Validation

Required evidence:

- Backend and frontend verification
- Data-quality results
- Anomaly precision, recall and F1 where labels exist
- Forecast MAE, RMSE and WAPE
- Stockout and overstock detection results
- Recommendation acceptance and override rates
- User trust and explainability ratings
- Operational time comparisons

The repository must not report simulated demonstration counts as institutional performance results.

## Chapter 7 — Discussion

Discuss:

- Whether AI improves prioritisation
- Whether explanations improve trust
- Forecasting usefulness and uncertainty
- Institutional deployment implications
- Human governance requirements
- Data-quality effects on model reliability
- Ethical limits of anomaly interpretation

## Chapter 8 — Conclusion

Summarise:

- Framework contribution
- Practical impact
- Empirical findings
- Limitations
- Future Sage/POS integration
- Future model improvement
