from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.menucategoryschema import MenuCategoryCreateRequest, MenuCategoryRead, MenuCategoryResponse, MenuCategoryListResponse, GenericResponse
from app.services.menucategory_service import MenuCategoryService

router = APIRouter(prefix="/menucategory", tags=["menucategory"])


@router.post("/create", response_model=MenuCategoryResponse)
def create_menu_category(
    payload: MenuCategoryCreateRequest,
    db: Session = Depends(get_db)
):
    category = MenuCategoryService().create(db, payload)
    return MenuCategoryResponse(
        status=True,
        message="Menu category created successfully",
        data=MenuCategoryRead.from_orm(category)
    )


@router.get("/list", response_model=MenuCategoryListResponse)
def list_menu_categories(db: Session = Depends(get_db)):
    categories = MenuCategoryService().get_all(db)
    return MenuCategoryListResponse(
        status=True,
        message="Menu categories fetched successfully",
        data=[MenuCategoryRead.from_orm(cat) for cat in categories]
    )


@router.get("/get/{category_id}", response_model=MenuCategoryResponse)
def get_menu_category(category_id: int, db: Session = Depends(get_db)):
    category = MenuCategoryService().get_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Menu category not found")

    return MenuCategoryResponse(
        status=True,
        message="Menu category fetched successfully",
        data=MenuCategoryRead.from_orm(category)
    )


@router.delete("/delete/{category_id}", response_model=GenericResponse)
def delete_menu_category(category_id: int, db: Session = Depends(get_db)):
    deleted = MenuCategoryService().delete(db, category_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Menu category not found")

    return GenericResponse(
        status=True,
        message="Menu category deleted successfully",
        data=None
    )
