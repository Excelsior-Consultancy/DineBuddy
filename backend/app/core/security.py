import hashlib

from passlib.context import CryptContext
from passlib.exc import PasswordValueError

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def _sha256(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    return pwd_context.hash(_sha256(password))


def verify_password(password: str, hashed_password: str) -> bool:
    """Return True if password matches hash, False otherwise. Never raises for invalid input."""
    try:
        return pwd_context.verify(_sha256(password), hashed_password)
    except PasswordValueError:
        # bcrypt rejects digests containing NULL bytes; treat as wrong password
        return False
