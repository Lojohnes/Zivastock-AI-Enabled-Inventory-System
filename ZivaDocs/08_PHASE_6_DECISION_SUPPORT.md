# Phase 6 — Explainable Decision Support and Human Governance

**Status:** Implemented incrementally  
**Git status:** Uncommitted; no GitHub repository or commit created

## Purpose

Phase 6 connects the intelligence outputs to operational recommendations while maintaining human control.

```text
AI detects a signal
    ↓
AI explains the evidence
    ↓
AI recommends an action
    ↓
Authorised manager reviews
    ↓
Approve / Reject / Override
    ↓
Action outcome is recorded
```

The recommendation engine does not autonomously modify inventory quantities or post adjustments.

## Implemented components

### Recommendation persistence

Added:

- `backend/app/models/recommendation.py`
- Alembic revision `010_recommendations.py`
- `database/migrations/V018__recommendations.sql`

New tables:

```text
ai_recommendations
recommendation_decisions
recommendation_outcomes
```

Recommendations store:

- Product and location
- Recommendation type
- Recommendation text
- Priority
- Evidence-strength score
- Evidence list
- Expected impact
- Related model version
- Status
- Creation and expiry timestamps

Decisions store:

- Recommendation
- Approved/rejected/overridden decision
- Deciding user
- Reason
- Override flag
- Timestamp

Outcomes store:

- Recommendation
- Actual action
- Outcome status
- Actual result
- Variance after action
- Whether stockout was avoided
- Recording user
- Timestamp

## Recommendation types

The service generates recommendations for:

### Targeted recount

Triggered by signals such as:

- High anomaly score
- Significant variance
- Frequent adjustments
- Count disagreement

### Investigate adjustment

Triggered by:

- High anomaly score
- Repeated manual adjustments

The wording asks management to review movement and receiving history. It does not assign blame.

### Replenishment review

Triggered by:

- High or critical stockout risk
- Low days of inventory

The recommended quantity is calculated from predicted demand, safety stock and current stock over a seven-day horizon.

### Reduce or transfer

Triggered by:

- Excess quantity
- Slow-moving stock
- Non-moving stock

The recommendation asks management to review procurement or consider an internal transfer. It does not perform a transfer automatically.

### Monitor

Generated when no high-priority signal is present, ensuring that every analysed item can still be represented in a management workflow.

## Evidence strength

The stored `confidence_score` represents **evidence coverage**, not artificial model confidence. It counts independent operational signals such as:

- Anomaly signal
- Variance signal
- Adjustment signal
- Stockout signal
- Excess-stock signal

This distinction is important for explainability and research validity.

## Human-in-the-loop workflow

### Approve

An authorised user accepts the recommendation for operational follow-up.

### Reject

An authorised user rejects the recommendation and can provide a reason.

### Override

An authorised user chooses a different decision. An override reason is mandatory.

### Outcome

After the action is performed, the user records:

- Actual action
- Success, partial, failed or not applicable status
- Actual result
- Variance after action
- Whether a stockout was avoided

Completed outcomes change the recommendation status to `COMPLETED`.

## API endpoints

Added:

```text
POST /api/v1/recommendations/generate
POST /api/v1/recommendations/{recommendation_id}/decision
POST /api/v1/recommendations/{recommendation_id}/outcome
```

The endpoints require an authenticated user. Existing RBAC should be extended with dedicated recommendation-review permissions before production deployment. The current prototype keeps the workflow available to authenticated users so the research demonstration can be executed with seeded environments.

## Governance principles

- AI recommendations never directly change inventory.
- A recommendation is not proof of misconduct.
- Evidence is displayed separately from the recommendation.
- Overrides require reasons.
- Decisions and outcomes are persisted.
- The original recommendation remains traceable after a decision.
- Operational adjustment posting remains controlled by the existing adjustment workflow.

## Migration

The current Alembic head is:

```text
010 (head)
```

Apply deliberately with:

```powershell
cd backend
$env:DEBUG='True'
python -m alembic upgrade head
```

The migration has not been automatically applied to the live database.

## Verification

Phase 6 tests cover:

- Explainable recommendation generation
- Targeted recount recommendations
- Adjustment investigation recommendations
- Replenishment recommendations
- Evidence-strength calculation
- Human decision recording
- Override-reason enforcement
- Outcome recording
- Recommendation completion status

Verification result:

```text
30 passed
```

Python compilation passed and the recommendation API routes were found in the generated OpenAPI document.

Existing non-blocking warnings remain for Pydantic schema configuration, SQLAlchemy's legacy `declarative_base` import and product response decimal serialisation.

## Research limitations

1. Recommendation rules are transparent heuristics and require user evaluation.
2. Evidence strength is not probabilistic model confidence.
3. Recommendation acceptance is not yet analysed statistically.
4. Outcomes are manually recorded until operational integrations are available.
5. Recommendation permissions need to be added to the institutional RBAC policy.
6. The AI Inventory Command Centre frontend has not yet been implemented.

## Next phase

Phase 7 should build the management-facing AI Inventory Command Centre and connect it to:

- Risk rankings
- Forecast charts
- Stockout and overstock exposure
- Explainable recommendations
- Pending decisions
- Outcome and feedback status
