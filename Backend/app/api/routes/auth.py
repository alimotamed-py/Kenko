from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from app.core.config import settings
from app.core.database import get_session
from app.models.user import User
from app.schemas.auth import RequestOTP, VerifyOTP, CurrentUserResponse
from app.dependencies import verify_refresh_csrf, get_current_user
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token_strict,
)

from app.services.otp import (
    generate_otp,
    store_otp,
    verify_otp,
)

from app.services.rate_limit import (
    OTP_IP_LIMIT,
    OTP_IP_WINDOW_SECONDS,
    OTP_VERIFY_IP_LIMIT,
    OTP_VERIFY_IP_WINDOW_SECONDS,
    OTP_MAX_ATTEMPTS,
    is_otp_rate_limited,
    set_otp_rate_limit,
    is_otp_blocked,
    increment_otp_attempts,
    reset_otp_attempts,
    check_rate_limit,
)

from app.services.token import (
    store_refresh_token,
    consume_refresh_token,
    revoke_refresh_token,
)

from app.services.csrf import (
    generate_csrf_token,
    store_csrf_token,
    revoke_csrf_token,
)




router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_token_cookie(response: JSONResponse, name: str, value: str, max_age: int, path: str) -> None:
    response.set_cookie(key=name, value=value, httponly=True, secure=settings.COOKIE_SECURE,
                        samesite=settings.COOKIE_SAMESITE, path=path, max_age=max_age)


def _set_auth_cookies(response: JSONResponse, access_token: str, refresh_token: str) -> None:
    _set_token_cookie(response=response, name=settings.ACCESS_TOKEN_COOKIE_NAME, value=access_token,
                      max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, path=settings.ACCESS_TOKEN_COOKIE_PATH)

    _set_token_cookie(response=response, name=settings.REFRESH_TOKEN_COOKIE_NAME, value=refresh_token,
                      max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                      path=settings.REFRESH_TOKEN_COOKIE_PATH)


def _set_csrf_cookie(response: JSONResponse, csrf_token: str) -> None:
    response.set_cookie(key=settings.CSRF_COOKIE_NAME, value=csrf_token, httponly=False,
                        secure=settings.COOKIE_SECURE, samesite=settings.COOKIE_SAMESITE,
                        path=settings.CSRF_COOKIE_PATH, max_age=settings.CSRF_TOKEN_EXPIRE_SECONDS)


@router.post("/request-otp")
def request_otp(request: Request, data: RequestOTP):
    phone_number = data.phone_number
    client_ip = request.client.host if request.client else "unknown"

    # IP-based rate limit
    check_rate_limit(key=f"rate_limit:otp:request:ip:{client_ip}", limit=OTP_IP_LIMIT, window=OTP_IP_WINDOW_SECONDS)

    # Phone-based cooldown
    if is_otp_rate_limited(phone_number):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Please wait before requesting another OTP.")

    otp = generate_otp()
    store_otp(phone_number=phone_number, otp=otp)
    reset_otp_attempts(phone_number)
    set_otp_rate_limit(phone_number)
    return {"success": True, "message": "OTP sent successfully."}


@router.post("/verify-otp")
def verify_otp_endpoint(request: Request, data: VerifyOTP, session: Session = Depends(get_session)):
    phone_number = data.phone_number
    client_ip = (request.client.host if request.client else "unknown")

    # IP-based rate limit
    check_rate_limit(
    key=f"rate_limit:otp:verify:ip:{client_ip}",
    limit=OTP_VERIFY_IP_LIMIT,
    window=OTP_VERIFY_IP_WINDOW_SECONDS,
    )

    # Check if user is temporarily blocked
    if is_otp_blocked(phone_number):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail=(
            "Too many invalid OTP attempts. "
            "Please request a new OTP later."))

    # Verify OTP
    is_valid = verify_otp(phone_number=phone_number, otp=data.otp)

    if not is_valid:
        attempts = increment_otp_attempts(phone_number)

        if attempts >= OTP_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Too many invalid OTP attempts. "
                    "Please request a new OTP later."
                ),
            )

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP.")

    # OTP is valid → reset failed attempts
    reset_otp_attempts(phone_number)

    # Find existing user
    statement = select(User).where(User.phone_number == phone_number)
    user = session.exec(statement).first()

    # Create user if not exists
    if user is None:
        user = User(phone_number=phone_number, is_verified=True)
        session.add(user)
        session.commit()
        session.refresh(user)

    else:
        user.is_verified = True
        session.add(user)
        session.commit()
        session.refresh(user)

    # Create Refresh Token first
    refresh_token, refresh_jti = create_refresh_token(user_id=user.id, user_type="user")

    # Create Access Token
    # session_jti points to the current refresh-token session
    access_token, _ = create_access_token(user_id=user.id, user_type="user", session_jti=refresh_jti)

    # Store Refresh Token in Redis
    store_refresh_token(jti=refresh_jti, user_id=user.id)

    # Generate and store CSRF Token
    csrf_token = generate_csrf_token()

    store_csrf_token(token=csrf_token, jti=refresh_jti)

    response = JSONResponse(content={"success": True, "message": "Login successful."})

    # Set Access + Refresh cookies
    _set_auth_cookies(response=response, access_token=access_token, refresh_token=refresh_token)

    # Set CSRF cookie
    _set_csrf_cookie(response=response, csrf_token=csrf_token)
    return response


@router.post("/refresh", dependencies=[Depends(verify_refresh_csrf)])
def refresh_access_token(request: Request, session: Session = Depends(get_session)):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required.")

    # Decode Refresh Token
    payload = decode_token_strict(token=refresh_token, expected_type="refresh")

    user_id = payload.get("user_id")
    refresh_jti = payload.get("jti")

    if not isinstance(user_id, int) or not isinstance(refresh_jti, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    # Consume old Refresh Token
    if not consume_refresh_token(jti=refresh_jti, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token has been revoked or already used.")

    # Revoke CSRF Token associated with old session
    revoke_csrf_token(jti=refresh_jti)

    # Find user
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")

    # Create new Refresh Token
    new_refresh_token, new_refresh_jti = create_refresh_token(user_id=user.id, user_type="user")

    # Create new Access Token
    access_token, _ = create_access_token(user_id=user.id, user_type="user", session_jti=new_refresh_jti)

    # Store new Refresh Token
    store_refresh_token(jti=new_refresh_jti, user_id=user.id)

    # Generate and store new CSRF Token
    new_csrf_token = generate_csrf_token()

    store_csrf_token(token=new_csrf_token, jti=new_refresh_jti)

    response = JSONResponse(content={"success": True, "message": "Token refreshed successfully."})

    # Replace Access + Refresh cookies
    _set_auth_cookies(response=response, access_token=access_token, refresh_token=new_refresh_token)

    # Replace CSRF cookie
    _set_csrf_cookie(response=response, csrf_token=new_csrf_token)
    return response


@router.post("/logout", dependencies=[Depends(verify_refresh_csrf)])
def logout(request: Request):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    # Revoke Refresh Token and CSRF Token
    if refresh_token:
        try:
            payload = decode_token_strict(token=refresh_token, expected_type="refresh")
            refresh_jti = payload.get("jti")
            if isinstance(refresh_jti, str):
                revoke_refresh_token(refresh_jti)
                revoke_csrf_token(refresh_jti)

        except HTTPException:
            pass

    response = JSONResponse(content={"success": True, "message": "Logout successful."})

    # Delete Access Token cookie
    response.delete_cookie(key=settings.ACCESS_TOKEN_COOKIE_NAME, path=settings.ACCESS_TOKEN_COOKIE_PATH)

    # Delete Refresh Token cookie
    response.delete_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, path=settings.REFRESH_TOKEN_COOKIE_PATH)

    # Delete CSRF Token cookie
    response.delete_cookie(key=settings.CSRF_COOKIE_NAME, path=settings.CSRF_COOKIE_PATH)
    return response


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user