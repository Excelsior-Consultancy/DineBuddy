from sqlalchemy.orm import Session
from fastapi import UploadFile, BackgroundTasks
from decimal import Decimal
import csv
import io
import json
from datetime import datetime, time
from sqlalchemy import or_, and_
from app.models.menu_items import MenuItem
from app.schemas.menu_items_schema import MenuItemCreate, MenuItemUpdate
from app.services.bulk_import_items_service import process_rows
from app.core.database import SessionLocal


# ------------------------------------------------
# CREATE
# ------------------------------------------------
def create_menu_item(db: Session, data: MenuItemCreate) -> MenuItem:
    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ------------------------------------------------
# GET BY ID (GLOBAL)
# ------------------------------------------------
def get_menu_item(db: Session, item_id: int) -> MenuItem | None:
    return db.query(MenuItem).filter(MenuItem.id == item_id).first()


# ------------------------------------------------
# GET BY ID (RESTAURANT SCOPED)
# ------------------------------------------------
def get_menu_item_for_restaurant(
    db: Session,
    restaurant_id: int,
    item_id: int,
) -> MenuItem | None:
    return (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )


# ------------------------------------------------
# LIST (Restaurant Scoped)
# ------------------------------------------------
def list_menu_items(
    db: Session,
    restaurant_id: int,
    category_id: int | None = None,
    only_currently_available: bool = True,
):
    query = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id
    )

    if category_id:
        query = query.filter(MenuItem.category_id == category_id)

    if only_currently_available:
        now = datetime.now().time()

        query = query.filter(
            MenuItem.is_available.is_(True),
            or_(
                # All-day items
                and_(
                    MenuItem.available_from.is_(None),
                    MenuItem.available_to.is_(None),
                ),
                # Time-windowed items
                and_(
                    MenuItem.available_from <= now,
                    MenuItem.available_to >= now,
                ),
            ),
        )

    return query.order_by(MenuItem.name.asc()).all()



# ------------------------------------------------
# UPDATE
# ------------------------------------------------
def update_menu_item(
    db: Session,
    item: MenuItem,
    data: MenuItemUpdate,
) -> MenuItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


# ------------------------------------------------
# DELETE
# ------------------------------------------------
def delete_menu_item(db: Session, item: MenuItem) -> None:
    db.delete(item)
    db.commit()


# ------------------------------------------------
# AVAILABILITY TOGGLE
# ------------------------------------------------
def update_menu_item_availability(
    db: Session,
    item: MenuItem,
    is_available: bool,
) -> MenuItem:
    item.is_available = is_available
    db.commit()
    db.refresh(item)
    return item


# ------------------------------------------------
# IMPORT (BACKGROUND TASKS)
# ------------------------------------------------
def start_import(
    job_id: int,
    restaurant_id: int,
    file: UploadFile,
    background_tasks: BackgroundTasks,
):
    filename = file.filename.lower()

    if filename.endswith(".csv"):
        content = file.file.read().decode("utf-8")
        background_tasks.add_task(_run_import_job, job_id, restaurant_id, "csv", content)
    elif filename.endswith(".json"):
        items = json.loads(file.file.read().decode("utf-8"))
        if not isinstance(items, list):
            raise ValueError("JSON must be an array")
        background_tasks.add_task(_run_import_job, job_id, restaurant_id, "json", items)
    else:
        raise ValueError("Only CSV or JSON supported")


def _run_import_job(job_id: int, restaurant_id: int, file_type: str, payload):
    """
    Runs the import in a background task with a new DB session.
    """
    db = SessionLocal()
    try:
        if file_type == "json":
            process_rows(db, job_id, restaurant_id, payload)
        else:  # CSV
            rows = list(csv.DictReader(io.StringIO(payload)))
            process_rows(db, job_id, restaurant_id, rows)
    finally:
        db.close()


