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
from io import StringIO
import json
import csv

from app.core.database import get_db, SessionLocal
from app.core.permission import require_roles
from app.core.dependencies import CurrentUser, check_restaurant_access
from app.models.user import UserRole
from app.schemas.menu_items_schema import (
    MenuItemCreate,
    MenuItemRead,
    MenuItemUpdate,
    MenuItemAvailabilityUpdate,
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
# IMPORT ROUTES (STATIC)
# =================================================
@router.post("/import", status_code=202)
def import_menu_items(
    restaurant_id: int,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    require_roles(current_user, (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN))
    check_restaurant_access(restaurant_id, current_user, db)

    job = bulk_import_items_service.create_job(db, restaurant_id)

    # Call service, let it handle background task
    bulk_import_items_service.start_import(
        db=db,
        job_id=job.id,
        restaurant_id=restaurant_id,
        file=file,
        background_tasks=background_tasks
    )

    return {"job_id": job.id, "status": job.status, "message": "Import started"}



@router.get("/import/{job_id}")
def get_import_job_status(
    restaurant_id: int,
    job_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    check_restaurant_access(restaurant_id, current_user, db)

    return bulk_import_items_service.get_import_job(
        db=db,
        job_id=job_id,
        restaurant_id=restaurant_id,
    )


# =================================================
# MENU ITEM CRUD
# =================================================
@router.get("/", response_model=list[MenuItemRead])
def list_menu_items(
    restaurant_id: int,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    return menu_items_service.list_menu_items(
        db=db,
        restaurant_id=restaurant_id,
        category_id=category_id,
    )


@router.post("/", response_model=MenuItemRead)
def create_menu_item(
    restaurant_id: int,
    data: MenuItemCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    require_roles(
        current_user,
        (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN),
    )

    check_restaurant_access(restaurant_id, current_user, db)

    data.restaurant_id = restaurant_id
    return menu_items_service.create_menu_item(db, data)


@router.patch("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
    data: MenuItemUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    require_roles(
        current_user,
        (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN),
    )

    check_restaurant_access(restaurant_id, current_user, db)

    item = menu_items_service.get_menu_item_for_restaurant(
        db=db,
        item_id=item_id,
        restaurant_id=restaurant_id,
    )

    return menu_items_service.update_menu_item(db, item, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    restaurant_id: int,
    item_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    require_roles(
        current_user,
        (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN),
    )

    check_restaurant_access(restaurant_id, current_user, db)

    item = menu_items_service.get_menu_item_for_restaurant(
        db=db,
        item_id=item_id,
        restaurant_id=restaurant_id,
    )

    menu_items_service.delete_menu_item(db, item)


# =================================================
# AVAILABILITY
# =================================================
@router.patch("/{item_id}/availability", response_model=dict)
def update_menu_item_availability(
    restaurant_id: int,
    item_id: int,
    data: MenuItemAvailabilityUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    require_roles(
        current_user,
        (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN),
    )

    check_restaurant_access(restaurant_id, current_user, db)

    item = menu_items_service.get_menu_item_for_restaurant(
        db=db,
        item_id=item_id,
        restaurant_id=restaurant_id,
    )

    menu_items_service.update_menu_item_availability(
        db=db,
        item=item,
        is_available=data.is_available,
    )

    # Real-time event (placeholder)
    from app.core.events import notify_customers
    notify_customers(
        restaurant_id=restaurant_id,
        event="menu_item_availability_updated",
        payload={
            "item_id": item.id,
            "is_available": item.is_available,
        },
    )

    return {
        "item_id": item.id,
        "is_available": item.is_available,
        "status": "updated",
    }
