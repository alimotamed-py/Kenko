import secrets
from app.core.config import settings
from app.core.redis import redis_client


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def store_csrf_token(token: str, jti: str) -> None:
    key = f"csrf:{jti}"
    redis_client.set(key, token, ex=settings.CSRF_TOKEN_EXPIRE_SECONDS)


def verify_csrf_token(token: str, jti: str) -> bool:
    key = f"csrf:{jti}"
    stored_token = redis_client.get(key)
    if stored_token is None:
        return False
    return secrets.compare_digest(stored_token, token)


def revoke_csrf_token(jti: str) -> None:
    key = f"csrf:{jti}"
    redis_client.delete(key)