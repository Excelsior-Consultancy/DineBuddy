from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User, UserRole


class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Default values
        request.state.user = None
        request.state.restaurant_ids = []
        request.state.is_admin = False

        # Example: get user_id from header (JWT later)
        user_id = request.headers.get("User-Id")

        if user_id:
            db: Session = SessionLocal()
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    request.state.user = user
                    request.state.is_admin = user.role == UserRole.ADMIN

                    if user.role == UserRole.RESTAURANT_STAFF:
                        request.state.restaurant_ids = [
                            r.id for r in user.restaurants
                        ]
            finally:
                db.close()

        response = await call_next(request)
        return response
