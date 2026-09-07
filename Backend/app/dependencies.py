from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.models.user import User
from app.security.jwt import decode_token_strict
from app.services.csrf import verify_csrf_token


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:

    access_token = request.cookies.get(
        settings.ACCESS_TOKEN_COOKIE_NAME
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    payload = decode_token_strict(
        token=access_token,
        expected_type="access",
    )

    user_id = payload.get("user_id")

    if not isinstance(user_id, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    user = session.exec(
        select(User).where(User.id == user_id)
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


def verify_csrf(
    request: Request,
) -> None:

    csrf_token = request.headers.get(
        settings.CSRF_HEADER_NAME
    )

    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token is required.",
        )

    access_token = request.cookies.get(
        settings.ACCESS_TOKEN_COOKIE_NAME
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    payload = decode_token_strict(
        token=access_token,
        expected_type="access",
    )

    session_jti = payload.get("session_jti")

    if not isinstance(session_jti, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    if not verify_csrf_token(
        token=csrf_token,
        jti=session_jti,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token.",
        )


def verify_refresh_csrf(
    request: Request,
) -> None:

    csrf_token = request.headers.get(
        settings.CSRF_HEADER_NAME
    )

    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token is required.",
        )

    refresh_token = request.cookies.get(
        settings.REFRESH_TOKEN_COOKIE_NAME
    )

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required.",
        )

    payload = decode_token_strict(
        token=refresh_token,
        expected_type="refresh",
    )

    refresh_jti = payload.get("jti")

    if not isinstance(refresh_jti, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if not verify_csrf_token(
        token=csrf_token,
        jti=refresh_jti,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token.",
        )