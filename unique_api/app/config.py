from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # OIDC Provider Configuration
    ISSUER: str = "https://auth.uniproject.jp"
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "your-secret-key")  # 本番環境では必ず環境変数で設定する

    # Token Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ID_TOKEN_EXPIRE_MINUTES: int = 60

    # Security Configuration
    REQUIRE_TLS: bool = True
    REQUIRE_CLIENT_AUTH: bool = True
    SECURE_COOKIES: bool = True

    # Development Configuration
    DEBUG: bool = False


settings = Settings()
