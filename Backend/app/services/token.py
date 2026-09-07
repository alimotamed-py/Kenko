import json
from app.core.config import settings
from app.core.redis import redis_client


REFRESH_TOKEN_PREFIX = "refresh_token:"


def _get_refresh_token_key(jti: str) -> str:
    return f"{REFRESH_TOKEN_PREFIX}{jti}"


def store_refresh_token(jti: str, user_id: int) -> None:
    key = _get_refresh_token_key(jti)
    redis_client.set(key, json.dumps({"user_id": user_id}), ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)


def consume_refresh_token(jti: str, user_id: int) -> bool:
    key = _get_refresh_token_key(jti)
    data = redis_client.getdel(key)

    if data is None:
        return False

    try:
        token_data = json.loads(data)
    except json.JSONDecodeError:
        return False

    return token_data.get("user_id") == user_id


def revoke_refresh_token(jti: str) -> None:
    key = _get_refresh_token_key(jti)

    redis_client.delete(key)