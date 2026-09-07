import secrets
from app.core.logging import logger
from app.core.redis import redis_client


OTP_EXPIRE_SECONDS = 120


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def store_otp(phone_number: str, otp: str) -> None:
    key = f"otp:{phone_number}"

    redis_client.set(key, otp, ex=OTP_EXPIRE_SECONDS)

    logger.info("OTP generated for phone=%s: %s", phone_number, otp)


def verify_otp(phone_number: str, otp: str) -> bool:
    key = f"otp:{phone_number}"

    stored_otp = redis_client.get(key)
    if stored_otp is None:
        return False

    if not secrets.compare_digest(stored_otp, otp):
        return False

    redis_client.delete(key)

    return True