# ZivaStock AI-Enabled Inventory Intelligence Platform
# User Manual and Training Guide

**Version:** Phase 10 research prototype  
**Audience:** Retail managers, stocktake supervisors, counters, inventory officers, system administrators and research evaluators  
**System:** ZivaStock AI-Enabled Inventory Intelligence Platform  
**Environment:** University institutional FMCG retail operations

---

## 1. Purpose of this manual

This manual explains how to use ZivaStock for:

- User access and account management
- Product and inventory management
- Stocktake planning and execution
- First and second counting
- Reconciliation and adjustments
- Inventory imports
- Operational reporting
- AI anomaly analysis
- Inventory risk prioritisation
- Demand and stockout analysis
- Overstock and slow-moving detection
- AI-generated recommendations
- Human approval, rejection and override
- AI Command Centre monitoring
- AI Model Laboratory experiments
- Scenario analysis
- Demonstration and research validation

The guide is written as a training document. It explains not only which button to use, but also why the workflow exists and what the user is responsible for.

---

## 2. Important operating principle

ZivaStock is a decision-support system.

The correct operating sequence is:

```text
AI detects
    ↓
AI explains
    ↓
AI predicts
    ↓
AI recommends
    ↓
Authorised human decides
    ↓
Action is performed
    ↓
Outcome is recorded
```

The AI must not be treated as an autonomous inventory controller.

An anomaly means:

> The observed inventory behaviour differs from an expected, historical or peer pattern.

It does **not** automatically mean:

- Theft
- Fraud
- Employee misconduct
- Supplier wrongdoing
- Incorrect human behaviour

Users must review the evidence before taking action.

---

## 3. System access

### 3.1 Frontend address

During local development, open:

```text
http://localhost:3000
```

The frontend requires the backend API to be available at:

```text
http://127.0.0.1:8000
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### 3.2 Starting the system

#### Start the backend

Open PowerShell:

```powershell
cd "C:\Users\Administrator\Desktop\MASTER INFOR SYSTEMS Level 1.2\ZivaStock-AI-Enabled-System\backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start the frontend

Open a second PowerShell window:

```powershell
cd "C:\Users\Administrator\Desktop\MASTER INFOR SYSTEMS Level 1.2\ZivaStock-AI-Enabled-System\frontend"
npm run dev
```

Then open:

```text
http://localhost:3000
```

The project also contains a Windows startup script:

```powershell
cd "C:\Users\Administrator\Desktop\MASTER INFOR SYSTEMS Level 1.2\ZivaStock-AI-Enabled-System"
.\start_system.ps1
```

Use the startup script only when it is acceptable for it to stop existing Python and Node processes.

### 3.3 First login

1. Open the frontend URL.
2. Enter the email address supplied by the system administrator.
3. Enter your password.
4. Select **Sign In**.
5. On successful authentication, the system opens the Dashboard.

The system uses JWT access and refresh tokens. Avoid sharing tokens, passwords or screenshots containing sensitive information.

### 3.4 Registration

If self-registration is enabled:

1. Select **Register** on the login page.
2. Enter first name.
3. Enter last name.
4. Enter email address.
5. Enter a password of at least eight characters.
6. Confirm the password.
7. Select **Create account**.

New accounts receive the default configured role. An administrator should review the account and assign the correct operational permissions.

### 3.5 Logging out

1. Select the user avatar in the top-right corner.
2. Select **Logout**.

Always log out when using a shared or stocktake device.

---

## 4. User roles and responsibilities

The exact role names and permissions depend on the database configuration. The following operating model is recommended.

| Role | Main responsibilities |
|---|---|
| System Administrator | Users, roles, permissions, system configuration, migration and support |
| Inventory Manager | Stocktake approval, reconciliation, adjustments, AI review and decisions |
| Stocktake Supervisor | Create sessions, assign counters, monitor progress and resolve counting issues |
| First Counter | Perform assigned first counts using web or Android workflows |
| Second Counter | Independently perform second counts for assigned products/sections |
| Inventory Analyst | Imports, reports, data quality, model evaluation and validation |
| Research Evaluator | Model laboratory, experiments, scenarios and evidence review |
| Viewer/Manager | Read dashboards, reports, risk scores and recommendations |

### 4.1 Segregation of duties

A user who performs the first count for an assigned product/section should not perform the second count for the same scope.

This protects count independence and improves reconciliation reliability.

### 4.2 AI decision responsibility

Only authorised users should approve, reject or override AI recommendations.

A user must:

- Read the evidence
- Check the product and location
- Consider current operational context
- Record a reason when rejecting or overriding
- Record the outcome after the action is completed

---

## 5. Navigation overview

The main navigation contains the following areas.

| Menu item | Purpose |
|---|---|
| Dashboard | Operational stocktake KPIs and session progress |
| AI Command Centre | AI risk, exposure and recommendation monitoring |
| AI Model Laboratory | Model registry, metrics, scenarios and outcome analytics |
| Stocktake | Create and manage stocktake sessions |
| Products | Product catalogue and inventory master data |
| Import Inventory | Upload product or inventory files |
| Reports | Operational and reconciliation reports |
| Counts | Review first and second counts |
| Users | User administration |
| Roles & Permissions | Role and access control |
| Profile | Current-user profile |
| Settings | User/system preferences where enabled |

The application is responsive. On smaller screens, use the menu button to open the navigation drawer.

---

## 6. Dashboard

### 6.1 Dashboard purpose

The Dashboard provides an operational overview of the existing ZivaStock platform.

It is different from the AI Command Centre:

- **Dashboard:** What is happening with stocktake operations?
- **AI Command Centre:** Which inventory risks require management attention?

### 6.2 Dashboard indicators

Typical indicators include:

- Total sessions
- Active sessions
- Completed sessions
- Products
- Total counts
- Recent counts
- Pending duplicates
- Section completion
- Active users
- Recent stocktake sessions

### 6.3 Using the Dashboard

1. Open **Dashboard**.
2. Review active and paused stocktake sessions.
3. Check section completion.
4. Check pending duplicates.
5. Identify sessions that require supervisor attention.
6. Select **Stocktake** or **Reports** for operational follow-up.

The Dashboard does not replace reconciliation or AI analysis.

---

## 7. Product management

### 7.1 View products

1. Open **Products**.
2. Search by product description, barcode, SKU or product code where supported.
3. Review:
   - Product description
   - Barcode
   - Product code
   - Unit of measure
   - System quantity
   - Unit cost
   - Selling price
   - Reorder level
   - Category
4. Select a product row to view or edit details, subject to permissions.

### 7.2 Product data requirements

Before running AI analysis, product data should be as complete as possible.

Important fields include:

- Unique barcode
- Product code
- Description
- Unit of measure
- Unit cost
- System quantity
- Category
- Reorder level

Poor product master data can produce:

- Unresolved imports
- Incorrect financial exposure
- Incorrect ABC classification
- Incorrect product matching
- Unreliable forecasts

### 7.3 Product data rules

Do not create duplicate products for the same barcode.

If a product description changes, update the product master rather than creating a second product record.

---

## 8. Importing inventory and transaction data

### 8.1 Product imports through the frontend

1. Open **Import Inventory**.
2. Select the appropriate file.
3. Use CSV or Excel format.
4. Confirm that the file has a usable header row.
5. Review detected columns.
6. Map file columns to system fields.
7. Process the import.
8. Review successful and failed records.
9. Correct rejected records and import them again where appropriate.

### 8.2 Transaction event imports

The AI event ingestion API accepts CSV or Excel POS/ERP-style movement data.

Endpoint:

```text
POST /api/v1/inventory-events/ingest
```

Required logical fields include:

```text
source_record_id
event_type
quantity
event_timestamp
```

A product must be resolvable by one of:

```text
product_id
barcode
SKU
product_code
```

Supported event types include:

```text
SALE
PURCHASE
RECEIPT
RETURN
TRANSFER
STOCKTAKE
COUNT
ADJUSTMENT
WASTE
DAMAGE
PRICE_CHANGE
LOCATION_CHANGE
OPENING_BALANCE
CLOSING_BALANCE
```

### 8.3 Column mapping

If external column names differ from system names, provide a mapping such as:

```json
{
  "source_record_id": "TransactionNo",
  "barcode": "ItemCode",
  "event_type": "MovementType",
  "quantity": "Qty",
  "event_timestamp": "TransactionDate"
}
```

### 8.4 Data quality preview

Before importing event data, use:

```text
POST /api/v1/inventory-events/quality
```

The data-quality pipeline checks:

- Missing required fields
- Invalid event types
- Negative quantities
- Invalid dates
- Future dates
- Duplicate records
- Invalid products
- Invalid locations

Review the quality score and issue details before using the data for AI analysis.

### 8.5 Duplicate protection

Each event should contain a stable source identifier.

The system uses:

```text
source_system + source_record_id
```

to prevent the same source transaction from being imported twice.

Do not generate a new source ID every time a file is reprocessed.

---

## 9. Stocktake training workflow

The standard stocktake workflow is:

```text
Create session
    ↓
Assign users and sections
    ↓
Start session
    ↓
First count
    ↓
Second count
    ↓
Compare counts
    ↓
Reconcile discrepancies
    ↓
Generate adjustment
    ↓
Approve or reject adjustment
    ↓
Post approved adjustment
    ↓
Complete/archive session
```

### 9.1 Create a stocktake session

1. Open **Stocktake**.
2. Select **Create session**.
3. Enter a session name.
4. Select the location.
5. Select session type, such as full or cycle count.
6. Enter an optional description.
7. Save the session.

### 9.2 Assign counters

1. Open the new session.
2. Select **Assignments**.
3. Assign first counters to sections.
4. Assign second counters independently.
5. Confirm that the same person is not assigned to both count roles for the same scope.
6. Save assignments.

### 9.3 Start the session

1. Confirm the product and location scope.
2. Confirm counter assignments.
3. Select **Start**.
4. Inform counters that counting may now begin.

Avoid changing the physical inventory during a controlled stocktake unless the business procedure explicitly allows it. If movement continues, record the timing and operational procedure.

### 9.4 First count

First counters should:

1. Open the assigned session on the web or Android application.
2. Open the assigned shelf/section.
3. Scan or select the product.
4. Confirm the product barcode and description.
5. Enter the physical quantity.
6. Save the count.
7. Continue until the assigned section is complete.

A counter should not guess quantities. If the product cannot be identified, record the issue for the supervisor.

### 9.5 Second count

Second counters should:

1. Open the assigned session.
2. Work independently from the first counter.
3. Scan or select the product.
4. Confirm the physical quantity.
5. Save the second count.

The second count exists to provide an independent verification, not to copy the first count.

### 9.6 Offline Android counting

The Android app supports:

- Login
- Barcode scanning
- Local Room storage
- Offline count capture
- Background synchronisation
- Sync status monitoring

Offline workflow:

```text
Log in before entering low-connectivity area
    ↓
Synchronise product/session data
    ↓
Perform counts offline
    ↓
Return to network coverage
    ↓
Run synchronisation
    ↓
Review successful and failed records
```

If a sync item fails:

1. Open the sync status screen.
2. Review the error message.
3. Confirm the session and product data still exist.
4. Retry synchronisation.
5. Escalate unresolved failures to the supervisor.

Do not uninstall or clear application data before failed records have been recovered.

### 9.7 Reconciliation

1. Open the completed counting section.
2. Compare first and second quantities.
3. Identify mismatches.
4. Review the physical location again where necessary.
5. Check product identity and unit of measure.
6. Confirm the final quantity.
7. Generate or review the adjustment.

### 9.8 Adjustments

An adjustment contains:

- System quantity
- Final quantity
- Variance quantity
- Unit-cost snapshot
- Variance value
- Adjustment type
- Reason
- Approval status

Approval workflow:

```text
Pending
    ↓
Approved or rejected
    ↓
Posted if approved
```

Posting updates the product inventory quantity. Only authorised users should post adjustments.

---

## 10. Reports

Open **Reports** to review operational reports such as:

- Variance
- Session progress
- First counts
- Second counts
- Comparison
- Consolidated counts
- Duplicates
- Missing stock
- Productivity
- Audit trail
- Historical stocktake

Use reports to support investigation and evidence gathering. Do not treat a report as a replacement for checking the underlying records.

### 10.1 Recommended report sequence after stocktake

1. Session progress
2. Comparison report
3. Variance report
4. Duplicate report
5. Missing stock report
6. Adjustment summary
7. Audit report

---

## 11. AI Inventory Command Centre

Open:

```text
/command-centre
```

### 11.1 Command Centre KPIs

Review:

- Critical risks
- High risks
- Stockout risks
- Excess inventory
- Pending decisions
- Data-quality score

### 11.2 Risk table

The risk table displays:

- Product
- Risk level
- Total score
- ABC class
- Priority

Use the search box to find a product.

Use risk filters to show:

- All
- Critical
- High
- Medium

Select a row to open product intelligence details.

### 11.3 Stockout exposure

Review:

- Days of cover
- Predicted daily demand
- Stockout risk
- Stockout date where available

A critical stockout should be reviewed before low-priority administrative work.

### 11.4 Recommendations

Each recommendation includes:

- Action type
- Product
- Priority
- Recommendation text
- Evidence coverage
- Review action

Select **Review** to inspect evidence and decide.

### 11.5 Product intelligence

Product details include:

- Product identity
- Barcode
- Unit cost
- Risk explanation
- Exposure records
- Recommendation history

Use this view to answer:

> Why is this product high risk?

---

## 12. AI recommendations and human decisions

### 12.1 Recommendation types

The system may recommend:

- Targeted recount
- Investigate adjustment
- Replenishment review
- Reduce or transfer stock
- Monitor

### 12.2 Approve

Use **Approve** when:

- Evidence is sufficient
- The recommendation is operationally appropriate
- No conflicting action is already in progress

Record the operational action and later record the outcome.

### 12.3 Reject

Use **Reject** when:

- The recommendation is not appropriate
- A known operational explanation exists
- The product is already covered by another plan
- The evidence is insufficient

Provide a clear reason.

### 12.4 Override

Use **Override** when you choose a different decision from the AI recommendation.

An override reason is mandatory.

Examples:

- Supplier delivery already scheduled
- Product is being discontinued
- Planned internal transfer exists
- Physical recount already completed

### 12.5 Record the outcome

After the action:

1. Record the actual action.
2. Select outcome status.
3. Enter the result.
4. Enter variance after action where applicable.
5. Record whether stockout was avoided where applicable.

Outcome statuses:

```text
PENDING
SUCCESS
PARTIAL
FAILED
NOT_APPLICABLE
```

---

## 13. AI Model Laboratory

Open:

```text
/model-laboratory
```

### 13.1 Model registry

Review:

- Registered models
- Algorithms
- Versions
- Dataset versions
- Feature-set versions
- Status
- Evaluation metrics

A blank registry means models have not yet been persisted from an experiment. It does not mean the system should invent performance values.

### 13.2 Anomaly model comparison

The backend supports comparison of:

- Rule-based detection
- Statistical Z-score detection
- Isolation Forest

When confirmed labels exist, compare:

- Precision
- Recall
- F1-score
- False positives
- False negatives

### 13.3 Forecast scenario

Enter:

- Current stock
- Predicted daily demand
- Safety stock
- Horizon days
- Demand change percentage
- Supplier delay days

Select **Run scenario**.

Review:

- Stockout risk
- Days until stockout
- Ending quantity
- Stock projection chart

Do not describe scenario output as a probability unless the model explicitly produces a calibrated probability.

### 13.4 Recommendation outcome analytics

Review:

- Approved recommendations
- Rejected recommendations
- Overridden recommendations
- Completed recommendations
- Successful outcomes
- Pending decisions
- Success percentage

These indicators support future usability and trust evaluation.

---

## 14. Transaction simulator training workflow

The simulator is a research and demonstration tool, not a replacement POS.

Run:

```powershell
cd backend
python scripts\generate_transaction_dataset.py `
  --days 60 `
  --scenario abnormal_adjustment `
  --seed 42 `
  --output ..\imports\simulated_transactions.csv
```

Available scenarios:

```text
normal
high_demand
abnormal_adjustment
stock_discrepancy
supplier_delay
```

For the complete demonstration pipeline:

```powershell
python scripts\run_demo_pipeline.py `
  --days 60 `
  --seed 42 `
  --output ..\reports\demo_phase9
```

The output is simulated. Label it clearly in all presentations and dissertation materials.

---

## 15. Data governance and ethics

Users must:

- Use the minimum personal data necessary.
- Protect user and audit information.
- Avoid copying confidential records into screenshots.
- Treat anomalies as investigation signals.
- Avoid employee profiling without approval.
- Keep institutional and simulated datasets separate.
- Document data permissions and anonymisation.
- Ensure AI decisions remain reviewable by authorised humans.

### 15.1 What the system must not say

Avoid:

> Employee X stole inventory.

Use:

> Anomalous inventory behaviour detected. Review movement, count and receiving evidence.

---

## 16. Troubleshooting

### Cannot open the frontend

Check that Vite is running:

```powershell
npm run dev
```

Open:

```text
http://localhost:3000
```

### API connection error

Check that FastAPI is running on port 8000:

```text
http://127.0.0.1:8000/health
```

### Login fails

Check:

- Email address
- Password
- User active status
- User lock status
- Backend availability

Contact an administrator if the account is locked.

### Dashboard has no data

Check:

- Database connection
- Seed data
- User permissions
- Backend logs
- Migration state

### AI Command Centre is empty

The Command Centre reads persisted risk, exposure and recommendation records.

Check:

1. Migrations are applied through revision 010.
2. Demonstration or institutional data has been loaded.
3. Feature generation has run.
4. Anomaly detection has run.
5. Risk scoring has run.
6. Forecast/exposure processing has run.
7. Recommendations have been generated and persisted.

### Model Laboratory is empty

Run an experiment that persists model versions, or use the API model registry endpoint:

```text
GET /api/v1/anomalies/models
```

### Recommendation decision fails

Check:

- Recommendation is still PENDING.
- Override has a reason.
- User is authenticated.
- Recommendation record exists.
- Backend migration 010 is applied.

### Sync failures on Android

Check:

- Network connection
- API base URL
- Product/session availability
- Sync queue error message
- Duplicate client identifiers

Retry after confirming the source record has not already been accepted.

### Import errors

Review:

- Required headers
- Date formats
- Product identifiers
- Duplicate source record IDs
- Negative quantities
- Units of measure
- Location names

Use the data-quality preview before repeating a large import.

---

## 17. Daily manager operating routine

### Start of day

1. Open Dashboard.
2. Open AI Command Centre.
3. Review critical and high risks.
4. Review stockout exposures.
5. Review pending recommendations.
6. Assign investigation or recount work.

### During the day

1. Monitor new stocktake activity.
2. Review incoming inventory movements.
3. Check data-quality alerts.
4. Review recommendation decisions.
5. Record actions taken.

### End of day

1. Record recommendation outcomes.
2. Review failed or overridden actions.
3. Check unresolved stockout exposures.
4. Export reports where required.
5. Confirm sync queues are clear.

---

## 18. Examiner demonstration script

1. Log in.
2. Open **AI Command Centre**.
3. Select the highest-risk product.
4. Show the risk score and ABC classification.
5. Explain the anomaly evidence.
6. Show stockout exposure.
7. Show the recommendation.
8. Open the decision dialog.
9. Approve, reject or override the recommendation.
10. Open **AI Model Laboratory**.
11. Show model versions and metrics.
12. Run a demand-increase scenario.
13. Run a supplier-delay scenario.
14. Explain that AI recommends but a human decides.
15. Show the validation evidence package.

Core message:

```text
Detect → Explain → Predict → Recommend → Decide → Learn
```

---

## 19. Quick reference

| Task | Location/API |
|---|---|
| Login | `/login` |
| Dashboard | `/dashboard` |
| AI Command Centre | `/command-centre` |
| AI Model Laboratory | `/model-laboratory` |
| Stocktake | `/stocktake` |
| Products | `/products` |
| Imports | `/import` |
| Reports | `/reports` |
| Counts | `/counts` |
| Backend health | `GET /health` |
| Event quality | `POST /api/v1/inventory-events/quality` |
| Event ingestion | `POST /api/v1/inventory-events/ingest` |
| Anomaly models | `GET /api/v1/anomalies/models` |
| Risk command centre | `GET /api/v1/risk/command-centre` |
| Forecast scenario | `POST /api/v1/forecast/scenario` |
| Recommendation generation | `POST /api/v1/recommendations/generate` |
| Recommendation decision | `POST /api/v1/recommendations/{id}/decision` |
| Recommendation outcome | `POST /api/v1/recommendations/{id}/outcome` |
