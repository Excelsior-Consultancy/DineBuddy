# app/core/auth.py
from passlib.context import CryptContext

# Configure bcrypt for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password for storage"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored hash"""
    return pwd_context.verify(password, hashed_password)
