from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Kenko API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "info"

    # JWT
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Cookies
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"

    ACCESS_TOKEN_COOKIE_PATH: str = "/"
    REFRESH_TOKEN_COOKIE_PATH: str = "/api/v1/auth"
    
    #CSRF
    CSRF_COOKIE_NAME: str = "csrf_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
    CSRF_COOKIE_PATH: str = "/"
    CSRF_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    # PostgreSQL
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "kenko_user"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "kenko_db"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Machine Learning
    model_path: str = "/app/ML/ML models/heart_disease_model.pkl"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        auth = (f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else "")

        return (f"redis://{auth}" f"{self.REDIS_HOST}:" f"{self.REDIS_PORT}/" f"{self.REDIS_DB}")


settings = Settings()