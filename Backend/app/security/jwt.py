import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status

from app.core.config import settings


def generate_jti() -> str:
    return str(uuid.uuid4())


def _build_payload(
    user_id: int,
    user_type: str,
    token_type: str,
    expires_delta: timedelta,
    session_jti: str | None = None,
) -> tuple[dict[str, Any], str]:

    jti = generate_jti()

    now = datetime.now(timezone.utc)
    exp = now + expires_delta

    payload = {
        "user_id": user_id,
        "user_type": user_type,
        "type": token_type,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    if session_jti is not None:
        payload["session_jti"] = session_jti

    return payload, jti


def create_access_token(
    user_id: int,
    user_type: str,
    session_jti: str,
) -> tuple[str, str]:

    payload, jti = _build_payload(
        user_id=user_id,
        user_type=user_type,
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        session_jti=session_jti,
    )

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, jti


def create_refresh_token(
    user_id: int,
    user_type: str,
) -> tuple[str, str]:

    payload, jti = _build_payload(
        user_id=user_id,
        user_type=user_type,
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, jti


def decode_token(
    token: str,
) -> dict[str, Any] | None:

    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require": [
                    "exp",
                    "iat",
                    "user_id",
                    "jti",
                    "type",
                    "user_type",
                ],
            },
        )

    except jwt.PyJWTError:
        return None


def decode_token_strict(
    token: str,
    expected_type: str,
) -> dict[str, Any]:

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return payload