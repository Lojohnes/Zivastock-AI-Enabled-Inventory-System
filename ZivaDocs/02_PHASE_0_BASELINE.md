# Phase 0 — Baseline Stabilisation

**Project:** ZivaStock AI-Enabled Inventory Intelligence Framework  
**Status:** Completed with documented residual warnings  
**No Git commit created.**

## Objectives

Phase 0 establishes a reproducible baseline before adding the inventory-intelligence modules. It focuses on stabilising the current ZivaStock implementation, correcting test drift and verifying the existing backend, frontend and Android components.

## Changes completed

### 1. Test configuration

Added `backend/tests/conftest.py` to provide a lightweight SQLite test fixture for the current ORM model set. The fixture:

- Registers all current models with SQLAlchemy metadata
- Creates only the tables required by the service tests
- Provides a per-test database session
- Handles the PostgreSQL-oriented `BigInteger` primary-key type for SQLite test execution
- Normalises invalid external `DEBUG` values in the test process only

Added `backend/pytest.ini` with the backend test path and Python import path.

### 2. Test drift correction

Updated the legacy count and report tests to match the current implementation:

- `Count` was replaced with `FirstCount` and `SecondCount`
- `Section` was replaced with `ShelfSection`
- `CountCreate` was replaced with `FirstCountCreate`
- Obsolete count service methods were replaced with current methods
- Report assertions were aligned with current report response structures
- Dashboard testing isolates the PostgreSQL reporting-view dependency in the unit-test fixture

### 3. Cross-database test compatibility

Updated the UUID and IP-address model declarations in:

- `backend/app/models/user.py`
- `backend/app/models/session.py`

The UUID fields now use SQLAlchemy's backend-neutral `Uuid` type. The IP address field retains PostgreSQL `INET` in production while using a SQLite-compatible variant during tests. PostgreSQL production behaviour is preserved.

### 4. Import-check correction

Updated `backend/check_imports.py` to import the current `FirstCount` and `SecondCount` model classes rather than the removed `Count` and `Duplicate` classes.

## Verification results

### Backend tests

Command:

```powershell
cd backend
python -m pytest -q
```

Result:

```text
11 passed
```

The suite still reports deprecation and serializer warnings. These are non-blocking and should be addressed during a later technical-debt pass.

### Backend import and syntax check

Command:

```powershell
cd backend
$env:DEBUG='True'
python check_imports.py
```

Result:

```text
All checks passed
```

### Python compilation

Command:

```powershell
cd backend
python -m compileall -q app main.py
```

Result:

```text
compileall: PASS
```

### Frontend build

Command:

```powershell
cd frontend
npm run build
```

Result:

```text
Build completed successfully
```

A Vite warning remains that the main JavaScript chunk is larger than 500 kB. This is a performance optimisation issue, not a build failure.

### Android build

Command:

```powershell
cd android-app
.\gradlew.bat :app:assembleDebug
```

The build proceeded through Android resource processing, Kotlin compilation and Java compilation. Existing warnings include deprecated Android APIs, unchecked Kotlin casts and an AndroidX/support-library migration warning. These are non-blocking and should be addressed separately from the dissertation intelligence work.

## Residual Phase 0 items

1. The backend currently has both `backend/main.py` and `backend/app/main.py`; `backend/main.py` is the canonical entry point used by the startup script and deployment documentation. The duplicate should be documented or consolidated in a later refactoring decision.
2. The production reporting layer depends on PostgreSQL views such as `v_session_progress`; the unit fixture intentionally does not reproduce every PostgreSQL reporting view.
3. Pydantic deprecation warnings remain in schema classes.
4. The frontend main bundle is larger than the recommended Vite threshold.
5. Android contains non-blocking deprecation, unchecked-cast and legacy dependency warnings.
6. Redis remains an optional runtime dependency and should be started when rate-limiting or cache behaviour is being validated.
7. No Git commit has been created, and no GitHub repository has been created or connected as part of this phase.

## Phase 0 conclusion

The existing system is sufficiently stable to begin Phase 1. The next implementation phase should introduce the unified inventory-event and transaction-import layer, while preserving the existing stocktake, reconciliation, synchronisation, security and audit workflows.
