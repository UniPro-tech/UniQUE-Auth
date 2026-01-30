from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # OIDC Provider Configuration
    ISSUER: str = "https://auth.uniproject.jp"
    FRONTEND_URL: str = "https://unique.uniproject.jp"

    # ---------- JWT Configuration ----------
    # JWT署名アルゴリズム (HS256 or RS256)によって設定箇所が変わります。
    # HS256 用の場合は JWT_SECRET_KEY を、 RS256 用の場合は RSA_PRIVATE_KEY_PATH と RSA_PUBLIC_KEY_PATH を設定してください。
    JWT_ALGORITHM: str = "RS256"  # "HS256" or "RS256"

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")

    RSA_PRIVATE_KEY_PATH: str | None = os.getenv(
        "RSA_PRIVATE_KEY_PATH", "/app/unique_api/rsa_private.pem"
    )  # 例: "path/to/private_key.pem"
    RSA_PUBLIC_KEY_PATH: str | None = os.getenv(
        "RSA_PUBLIC_KEY_PATH", "/app/unique_api/rsa_public.pem"
    )  # 例: "path/to/public_key.pem"

    # ---------- Token Configuration ----------
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ID_TOKEN_EXPIRE_MINUTES: int = 60

    # ---------- Security Configuration ----------
    REQUIRE_TLS: bool = True
    REQUIRE_CLIENT_AUTH: bool = True
    SECURE_COOKIES: bool = True

    # Development Configuration
    DEBUG: bool = False


settings = Settings()
