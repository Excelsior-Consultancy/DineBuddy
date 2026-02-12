from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.schemas.user_schema import UserLogin, Token
from app.services.user_service import login_user, refresh_tokens
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    tokens = login_user(
        db,
        payload.email,
        payload.password,
    )

    return tokens


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    """

    return refresh_tokens(db, refresh_token)
