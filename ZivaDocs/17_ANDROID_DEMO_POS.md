# Android Application and Demo POS

## Android application status

The existing Android application remains the operational offline-first stocktake client.

It supports:

- JWT login
- Room local storage
- Barcode scanning
- First/second counting workflows
- Offline capture
- WorkManager synchronisation
- Sync status monitoring
- Dashboard metrics
- Reports
- Role-aware navigation

### Android enhancement

The Android dashboard now includes an **AI inventory readiness** card.

It communicates:

- When local count changes are still waiting to synchronise
- When counts are synchronised and central AI analysis can process them
- That anomaly, risk and forecast results are centrally generated after synchronisation

This deliberately keeps AI analysis in the central platform rather than weakening offline reliability with an unnecessary edge-ML dependency.

### Build and run

Open `android-app` in Android Studio or build with:

```powershell
cd android-app
.\gradlew.bat :app:assembleDebug
```

The debug APK is generated under:

```text
android-app/app/build/outputs/apk/debug/app-debug.apk
```

For an emulator using the local backend:

```powershell
.\gradlew.bat assembleDebug -PapiBaseUrl=http://10.0.2.2:8000/api/v1/
```

### Android operating workflow

1. Log in while connected.
2. Synchronise products and stocktake assignments.
3. Open the assigned count workflow.
4. Scan a barcode.
5. Confirm product description and barcode.
6. Enter the physical quantity.
7. Save the count locally.
8. Continue counting without connectivity if required.
9. Return to network coverage.
10. Open Sync Status.
11. Retry failed records if necessary.
12. Confirm the dashboard readiness message.
13. Review AI results in the web Command Centre after central processing.

## Demo POS

The Demo POS is a safe research and demonstration simulator. It is not a replacement for Sage Evolution, ElitePOS or a production point-of-sale system.

### Frontend route

```text
/demo-pos
```

The page supports:

- Scenario selection
- Number of days
- Random seed
- Transaction generation
- Record count summary
- Sales count
- Receipt count
- Adjustment count
- Transaction value
- Scrollable transaction table
- CSV download
- One-click load into the AI pipeline
- Pipeline completion feedback with created event, risk, exposure and recommendation counts

### Scenarios

```text
normal
high_demand
abnormal_adjustment
stock_discrepancy
supplier_delay
```

### Demo POS API

```text
GET  /api/v1/demo-pos/generate
POST /api/v1/demo-pos/run-pipeline
```

`run-pipeline` creates the demo catalog/location if needed and runs the complete AI processing chain. It requires the Phase 1–6 tables to exist and the database migration state to be aligned.

Example parameters:

```text
scenario=abnormal_adjustment
days=60
seed=42
```

The generated data includes:

- Sales
- Receipts
- Returns
- Adjustments
- Product identifiers
- Event dates
- Quantities
- Unit costs
- Transaction values
- References

### Recommended demonstration

1. Open `/demo-pos`.
2. Select `abnormal_adjustment`.
3. Enter `60` days.
4. Enter seed `42`.
5. Generate transactions.
6. Review the adjustment record.
7. Select **Load & analyse in AI** to create the Demo POS products and run event ingestion, features, anomalies, risks, forecasts, exposures and recommendations.
8. Review the success summary.
9. Open `/command-centre`.
10. Select the highest-risk product.
11. Explain how the injected adjustment creates evidence for investigation.

All generated data must be labelled:

> Simulated POS/ERP data for research demonstration.

## Verification

- Android debug build: passed
- Frontend production build: passed
- Backend tests: passed
- Backend compilation: passed
- Demo POS API route: registered

Existing Android compiler warnings remain for deprecated Android APIs, unchecked casts and legacy dependency migration. These warnings do not prevent the debug build.
