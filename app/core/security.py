from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac
from secrets import compare_digest, token_hex

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessException
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = token_hex(16)
    password_hash = pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, expected_hash = password_hash.split("$", 1)
    except ValueError:
        return False
    actual_hash = pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return compare_digest(actual_hash, expected_hash)


def create_access_token(user_id: int) -> str:
    expire_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise BusinessException("NOT_AUTHENTICATED", "Authentication required", status.HTTP_401_UNAUTHORIZED)

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise BusinessException(
            "INVALID_TOKEN",
            "Invalid authentication token",
            status.HTTP_401_UNAUTHORIZED,
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise BusinessException("INVALID_TOKEN", "Invalid authentication token", status.HTTP_401_UNAUTHORIZED)
    return user

