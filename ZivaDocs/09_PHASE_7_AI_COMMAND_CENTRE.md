# Phase 7 — AI Inventory Command Centre

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 7 creates the management-facing interface for the inventory intelligence framework. It brings risk, exposure and recommendation outputs into one operational view without replacing the existing ZivaStock dashboard or stocktake workflow.

```text
Risk scores
    + Stockout exposure
    + Overstock exposure
    + Explainable recommendations
    + Human decisions
    ↓
AI Inventory Command Centre
```

## Backend command-centre data contract

Added GET endpoints to the existing risk API:

```text
GET /api/v1/risk/command-centre
GET /api/v1/risk/product/{product_id}
```

The command-centre response includes:

- Total products with risk scores
- Critical risks
- High risks
- Stockout risks
- Excess inventory count
- Pending recommendation count
- Top risk records
- Stockout exposure records
- Pending recommendations

The product intelligence response includes:

- Product identity
- Historical risk scores
- Exposure records
- Recommendation history

These endpoints read persisted Phase 4–6 outputs. They do not fabricate analytical results in the frontend.

## Frontend components

Added:

- `frontend/src/pages/InventoryCommandCentre.tsx`
- `frontend/src/services/intelligenceApi.ts`
- `frontend/src/types/intelligence.ts`

Updated:

- `frontend/src/App.tsx`
- `frontend/src/components/layout/Sidebar.tsx`

The new route is:

```text
/command-centre
```

The sidebar now includes:

```text
AI Command Centre
```

## Command Centre interface

### Executive KPIs

The page displays:

- Critical risks
- High risks
- Stockout risks
- Excess inventory
- Pending decisions

### Top inventory risks

The risk table displays:

- Product name
- Risk level
- Total risk score
- ABC class
- Priority

Selecting a product opens its intelligence detail view.

### Stockout exposure

The stockout panel displays:

- Product
- Days of cover
- Predicted daily demand
- Stockout risk

### Pending recommendations

Each recommendation displays:

- Recommendation type
- Priority
- Product
- Recommendation text
- Evidence coverage
- Review action
- Product details action

## Human decision interaction

The review dialog displays:

- Recommendation text
- Supporting evidence
- Governance warning
- Approve action
- Reject action
- Override action

Override actions require a reason through the decision workflow.

The UI explicitly states:

> AI recommends; an authorised manager must decide. An anomaly is not proof of misconduct.

## Product intelligence detail

The product dialog displays:

- Product identity
- Barcode
- Unit cost
- Risk explanations
- Stockout exposure
- Excess quantity
- Recommendation history

This supports the demonstration requirement of selecting a product and explaining why it is high risk.

## Verification

Frontend production build:

```text
Build completed successfully
```

Backend verification after adding the command-centre endpoints:

```text
30 passed
compileall: PASS
```

The frontend still reports the existing non-blocking Vite warning about the main JavaScript bundle being larger than 500 kB.

## Runtime dependency

The Command Centre requires:

1. Phase 1–6 migrations to be applied
2. Persisted risk scores, exposure records and recommendations
3. Authenticated access to the API
4. API base URL configured through the existing Axios service

If there are no persisted intelligence records, the Command Centre will display empty-state panels rather than invented values.

## Research relevance

Phase 7 makes the research implementation demonstrable by exposing the complete chain:

```text
Detect
    → Explain
    → Predict
    → Prioritise
    → Recommend
    → Manager decides
```

It provides the primary interface for usability, trust, explainability and decision-confidence evaluation.

## Limitations

1. The frontend currently uses persisted result endpoints and does not yet provide a full model-training laboratory.
2. Forecast charts are not yet rendered as time-series visualisations.
3. Recommendation outcomes are recorded through the backend but do not yet show longitudinal performance analytics.
4. Dedicated recommendation RBAC permissions should be added before production use.
5. The page has been build-verified but requires live browser testing with migrated and populated intelligence data.

## Next phase

Phase 8 should implement:

- AI Model Laboratory UI
- Forecast time-series charts
- Model comparison visualisations
- Recommendation outcome analytics
- What-if scenario controls
- Demonstration dataset orchestration
- Research validation evidence capture
