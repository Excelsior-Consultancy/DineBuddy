from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


def create_admin():
    db: Session = SessionLocal()

    email = "admin@dinebuddy.com"
    password = "admin123"   # CHANGE THIS
    name = "Super Admin"

    existing = db.query(User).filter(User.email == email).first()

    if existing:
        print("Admin already exists")
        return

    admin = User(
        email=email,
        full_name=name,
        password_hash=hash_password(password),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )

    db.add(admin)
    db.commit()

    print("Admin created successfully")


if __name__ == "__main__":
    create_admin()
