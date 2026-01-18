from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
import json
import csv
from io import StringIO

from app.core.database import get_db, SessionLocal
from app.core.dependencies import get_current_user, check_restaurant_access
from app.models.user import User, UserRole
from app.schemas.menu_items_schema import (
    MenuItemCreate,
    MenuItemRead,
    MenuItemUpdate,
    MenuItemAvailabilityUpdate
)
from app.services import (
    menu_items_service,
    bulk_import_items_service,
)

router = APIRouter(
    prefix="/restaurants/{restaurant_id}/menu-items",
    tags=["Restaurant Menu Items"],
)

# =================================================
# BACKGROUND TASK WRAPPER
# =================================================
def run_import_job(
    job_id: int,
    restaurant_id: int,
    file_type: str,
    payload,
):
    db = SessionLocal()
    try:
        if file_type == "json":
            # JSON payload is already a list of dicts
            bulk_import_items_service.process_rows(
                db=db,
                job_id=job_id,
                restaurant_id=restaurant_id,
                rows=payload,
            )
        else:  # CSV
            import csv, io
            # payload is the CSV content string
            rows = list(csv.DictReader(io.StringIO(payload)))
            bulk_import_items_service.process_rows(
                db=db,
                job_id=job_id,
                restaurant_id=restaurant_id,
                rows=rows,
            )
    finally:
        db.close()

# =================================================
# IMPORT ROUTES (STATIC — MUST BE FIRST)
# =================================================

@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
def import_menu_items(
    restaurant_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    if current_user.role == UserRole.RESTAURANT_ADMIN:
        check_restaurant_access(restaurant_id, current_user, db)

    job = bulk_import_items_service.create_job(db, restaurant_id)
    filename = file.filename.lower()

    # ---------- CSV ----------
    if filename.endswith(".csv"):
        content = file.file.read().decode("utf-8")
        csv.DictReader(StringIO(content))  # validate CSV

        background_tasks.add_task(
            run_import_job,
            job.id,
            restaurant_id,
            "csv",
            content,  # ✅ Pass the CSV content string, not the file
        )

    # ---------- JSON ----------
    elif filename.endswith(".json"):
        content = file.file.read().decode("utf-8")
        items = json.loads(content)
        if not isinstance(items, list):
            raise HTTPException(400, "JSON must be an array")

        background_tasks.add_task(
            run_import_job,
            job.id,
            restaurant_id,
            "json",
            items,  # ✅ Already a list of dicts
        )


    else:
        raise HTTPException(400, "Only CSV or JSON supported")

    return {
        "job_id": job.id,
        "status": job.status,
        "message": "Import started",
    }


@router.get("/import/{job_id}")
def get_import_job_status(
    restaurant_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.RESTAURANT_ADMIN:
        check_restaurant_access(restaurant_id, current_user, db)

    return bulk_import_items_service.get_import_job(
        db=db,
        job_id=job_id,
        restaurant_id=restaurant_id,
    )


# =================================================
# NORMAL MENU ITEM CRUD (DYNAMIC — MUST BE LAST)
# =================================================

@router.get("/", response_model=list[MenuItemRead])
def list_menu_items(
    restaurant_id: int,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    return menu_items_service.list_menu_items(
        db,
        restaurant_id=restaurant_id,
        category_id=category_id,
    )


@router.post("/", response_model=MenuItemRead)
def create_menu_item(
    restaurant_id: int,
    data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(403, "Not allowed")

    check_restaurant_access(restaurant_id, current_user, db)

    data.restaurant_id = restaurant_id
    return menu_items_service.create_menu_item(db, data)


@router.get("/{item_id}", response_model=MenuItemRead)
def get_menu_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(404, "Menu item not found")
    return item


@router.patch("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
    data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(404, "Menu item not found")

    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(403, "Not allowed")

    check_restaurant_access(restaurant_id, current_user, db)
    return menu_items_service.update_menu_item(db, item, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(404, "Menu item not found")

    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(403, "Not allowed")

    check_restaurant_access(restaurant_id, current_user, db)
    menu_items_service.delete_menu_item(db, item)


@router.patch("/{item_id}/availability", response_model=dict)
def update_menu_item_availability(
    restaurant_id: int,
    item_id: int,
    data: MenuItemAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get item
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Permission check
    if current_user.role not in (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN):
        raise HTTPException(status_code=403, detail="Not allowed")

    check_restaurant_access(restaurant_id, current_user, db)

    # Update availability
    updated_item = menu_items_service.update_menu_item_availability(
        db, item, data.is_available
    )

    # Emit real-time event (placeholder)
    # Replace with your actual WebSocket or push notification mechanism
    from app.core.events import notify_customers  # example
    notify_customers(
        restaurant_id=restaurant_id,
        event="menu_item_availability_updated",
        payload={"item_id": item.id, "is_available": item.is_available},
    )

    return {"item_id": item.id, "is_available": item.is_available, "status": "updated"}