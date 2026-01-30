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
from app.core.permission import require_roles
from app.core.database import get_db
from app.core.dependencies import CurrentUser, get_current_user, check_restaurant_access
from app.models.user import User, UserRole
from app.schemas.menu_items_schema import (
    MenuItemCreate,
    MenuItemRead,
    MenuItemUpdate,
)
from app.services import (
    menu_items_service,
    bulk_import_items_service,
)
from app.core.database import get_db, SessionLocal
import json
import csv
from io import StringIO
router = APIRouter(
    prefix="/restaurants/{restaurant_id}/menu-items",
    tags=["Restaurant Menu Items"],
)


# ------------------------------------------------------------------
# GET MENU ITEM BY ID (PUBLIC)
# ------------------------------------------------------------------
@router.get("/{item_id}", response_model=MenuItemRead)
def get_menu_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
):
    item = menu_items_service.get_menu_item(
        db,
        item_id=item_id,
        restaurant_id=restaurant_id,
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )

    return item


# =================================================
# IMPORT ROUTES (STATIC — MUST BE FIRST)
# =================================================

@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
def import_menu_items(
    restaurant_id: int,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    require_roles(
        current_user,
        (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN),
    )

    check_restaurant_access(restaurant_id, current_user, db)

    job = bulk_import_items_service.create_job(db, restaurant_id)

    bulk_import_items_service.start_import(
        job_id=job.id,
        restaurant_id=restaurant_id,
        file=file,
        background_tasks=background_tasks,
    )

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

# ------------------------------------------------------------------
# UPDATE MENU ITEM
# ------------------------------------------------------------------
@router.patch("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
    data: MenuItemUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    require_roles(current_user, (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN))
    check_restaurant_access(restaurant_id, current_user, db)

    item = menu_items_service.get_menu_item(
        db,
        item_id=item_id,
        restaurant_id=restaurant_id,
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )

    return menu_items_service.update_menu_item(db, item, data)


# DELETE MENU ITEM
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    restaurant_id: int,
    item_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    require_roles(current_user, (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN))
    check_restaurant_access(restaurant_id, current_user, db)

    item = menu_items_service.get_menu_item(
        db,
        item_id=item_id,
        restaurant_id=restaurant_id,
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )

    menu_items_service.delete_menu_item(db, item)


