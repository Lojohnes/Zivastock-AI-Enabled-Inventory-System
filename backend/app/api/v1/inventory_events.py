import json
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.services.data_quality_service import DataQualityService
from app.services.import_service import ImportService
from app.services.inventory_event_service import InventoryEventService

router = APIRouter()


@router.post("/quality")
async def profile_inventory_event_quality(
    file: UploadFile = File(...),
    source_system: str = Query(..., min_length=1, max_length=50),
    mapping_json: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Profile a transaction file without persisting inventory events."""
    del user_id
    try:
        mapping = json.loads(mapping_json) if mapping_json else None
        if mapping is not None and not isinstance(mapping, dict):
            raise ValueError("mapping_json must contain a JSON object")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid mapping_json: {exc}") from exc

    content = await file.read()
    try:
        dataframe = ImportService(db).read_import_file(content, file.filename or "")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse transaction file: {exc}") from exc
    assessment = DataQualityService(db).assess_dataframe(dataframe, source_system, mapping)
    return {key: value for key, value in assessment.items() if key != "issues"} | {"issues": assessment["issues"][:100]}


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_inventory_events(
    file: UploadFile = File(...),
    source_system: str = Query(..., min_length=1, max_length=50),
    mapping_json: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Parse and validate a CSV/Excel transaction file into inventory events."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="A transaction filename is required")

    try:
        mapping = json.loads(mapping_json) if mapping_json else None
        if mapping is not None and not isinstance(mapping, dict):
            raise ValueError("mapping_json must contain a JSON object")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid mapping_json: {exc}") from exc

    content = await file.read()
    import_service = ImportService(db)
    try:
        dataframe = import_service.read_import_file(content, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse transaction file: {exc}") from exc

    if dataframe.empty:
        raise HTTPException(status_code=400, detail="The transaction file contains no data rows")

    batch = import_service.create_import_batch(
        filename=file.filename,
        source="inventory_events",
        uploaded_by=user_id,
        total_records=len(dataframe),
    )
    batch.mapping_config = mapping or {}
    db.commit()

    try:
        result = InventoryEventService(db).ingest_dataframe(
            dataframe=dataframe,
            source_system=source_system,
            mapping=mapping,
            import_batch_id=batch.id,
        )
        import_service.update_import_batch(
            batch.id,
            "completed" if result["rejected_records"] == 0 else "completed_with_errors",
            result["accepted_records"],
            result["rejected_records"],
        )
    except Exception as exc:
        import_service.update_import_batch(batch.id, "failed", 0, len(dataframe))
        raise HTTPException(status_code=500, detail=f"Transaction ingestion failed: {exc}") from exc

    return {"import_batch_id": batch.id, **result}
