from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def _sha256(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).digest()

def hash_password(password: str) -> str:
    return pwd_context.hash(_sha256(password))

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_sha256(password), hashed_password)
