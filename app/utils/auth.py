from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.config.settings import settings
from app.utils.exceptions import AuthenticationException


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_user_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT for cookie authentication."""
    expire = datetime.now(UTC) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = data.copy()
    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def verify_user_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        exp = payload.get("exp")
        if exp is None:
            raise AuthenticationException("Token missing expiration")

        expiration = datetime.fromtimestamp(exp, tz=UTC)

        if datetime.now(UTC) > expiration:
            raise AuthenticationException("Token has expired")

        return payload

    except jwt.InvalidTokenError as exc:
        raise AuthenticationException("Token validation failed") from exc


def generate_user_token(user_data: dict[str, Any]) -> str:
    """Generate a JWT for a user."""
    return create_user_token(
        {
            "sub": str(user_data["id"]),
            "email": user_data["email"],
            "role": user_data.get("role", "USER"),
        }
    )