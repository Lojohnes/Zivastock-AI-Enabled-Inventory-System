import os
import py_compile
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

files = [
    "app/models/count.py",
    "app/models/sync.py",
    "app/models/import_batch.py",
    "app/services/report_service.py",
    "app/api/v1/reports.py",
    "app/schemas/count.py",
    "seed_data.py",
    "tests/test_report_service.py",
    "tests/test_count_service.py",
    "main.py",
]

for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"OK {f}")
    except Exception as e:
        print(f"FAIL {f}: {e}")
        sys.exit(1)

try:
    from app.models.count import FirstCount, SecondCount
    print("OK import app.models.count")
    from app.services.report_service import ReportService
    print("OK import app.services.report_service")
    from app.api.v1.reports import router
    print("OK import app.api.v1.reports")
    from main import app
    print("OK import main")
except Exception as e:
    print(f"FAIL import: {e}")
    sys.exit(1)

print("All checks passed")
