from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.schemas.user_schema import UserLogin, Token
from app.services.user_service import login_user
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    token = login_user(
        db,
        payload.email,
        payload.password,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
