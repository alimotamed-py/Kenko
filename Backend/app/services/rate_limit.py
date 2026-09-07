from fastapi import HTTPException, status

from app.core.redis import redis_client


def check_rate_limit(
    key: str,
    limit: int,
    window: int,
) -> None:
    """
    Fixed-window rate limiter using Redis.
    """

    count = redis_client.incr(key)

    if count == 1:
        redis_client.expire(key, window)

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )


# ---------------------------------
# OTP Rate Limits
# ---------------------------------

# Request OTP
OTP_COOLDOWN_SECONDS = 60

OTP_IP_LIMIT = 5
OTP_IP_WINDOW_SECONDS = 10 * 60


# Verify OTP
OTP_VERIFY_IP_LIMIT = 20
OTP_VERIFY_IP_WINDOW_SECONDS = 10 * 60

OTP_MAX_ATTEMPTS = 5
OTP_BLOCK_SECONDS = 5 * 60


# ---------------------------------
# OTP Phone Cooldown
# ---------------------------------

def is_otp_rate_limited(phone_number: str) -> bool:
    key = f"otp:cooldown:{phone_number}"

    return redis_client.exists(key) == 1


def set_otp_rate_limit(phone_number: str) -> None:
    key = f"otp:cooldown:{phone_number}"

    redis_client.set(
        key,
        "1",
        ex=OTP_COOLDOWN_SECONDS,
    )


# ---------------------------------
# OTP Failed Attempts
# ---------------------------------

def get_otp_attempts(phone_number: str) -> int:
    key = f"otp:attempts:{phone_number}"

    value = redis_client.get(key)

    if value is None:
        return 0

    return int(value)


def increment_otp_attempts(phone_number: str) -> int:
    key = f"otp:attempts:{phone_number}"

    attempts = redis_client.incr(key)

    if attempts == 1:
        redis_client.expire(
            key,
            OTP_BLOCK_SECONDS,
        )

    return attempts


def reset_otp_attempts(phone_number: str) -> None:
    key = f"otp:attempts:{phone_number}"

    redis_client.delete(key)


def is_otp_blocked(phone_number: str) -> bool:
    attempts = get_otp_attempts(phone_number)

    return attempts >= OTP_MAX_ATTEMPTS