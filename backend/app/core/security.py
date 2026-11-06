from datetime import datetime, timedelta, timezone
import hashlib
import unicodedata
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.core.errors import AppError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DUMMY_PASSWORD_HASH = "$2b$12$C6UzMDM.H6dfI/f/IKcEe.Vb1w8YJQjR3VQj5JfD7j0y7bZK8Yw2S"


def normalize_username(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def validate_username(value: str) -> str:
    value = value.strip()
    normalized = normalize_username(value)
    if len(normalized) < 3 or len(normalized) > 32 or not any(char.isalnum() for char in normalized):
        raise ValueError("username must be 3-32 characters and contain a letter or digit")
    if any(ord(char) < 32 for char in normalized):
        raise ValueError("username contains control characters")
    return value


def validate_password(value: str) -> str:
    byte_length = len(value.encode("utf-8"))
    if byte_length < 8 or byte_length > 72:
        raise ValueError("password must be 8-72 UTF-8 bytes")
    return value


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    return pwd_context.verify(password, password_hash or DUMMY_PASSWORD_HASH)


def create_access_token(user_id: int, username: str, token_version: int) -> tuple[str, datetime]:
    settings = get_settings()
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(days=settings.jwt_expire_days)
    payload = {
        "sub": str(user_id),
        "username": username,
        "token_version": token_version,
        "iat": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm), expires_at


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AppError(401, 40101, "未认证") from exc
    if not payload.get("sub") or "token_version" not in payload:
        raise AppError(401, 40101, "未认证")
    return payload


def username_digest(normalized_username: str) -> str:
    return hashlib.sha256(normalized_username.encode("utf-8")).hexdigest()[:16]
