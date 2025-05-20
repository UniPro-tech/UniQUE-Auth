import time
from pydantic import BaseModel, Field


class BaseToken(BaseModel):
    """
    UniQUEのトークンの基底クラス
    Args:

    """
    id: str = Field(
        ...,
        description="ユーザーのID(sub)",
        example="1234567890",
        max_length=255,
    )
    iss: str = Field(
        ...,
        description="発行者(iss)",
        example="https://example.com",
        max_length=255,
    )
    client_id: str = Field(
        ...,
        description="クライアントID(aud)",
        example="1234567890",
        max_length=255,
    )
    scope: str = Field(
        ...,
        description="スコープ(scope)",
        example="openid email profile",
        max_length=255,
    )
    exp: int = Field(
        ...,
        description="有効期限(exp)",
        example=int(time.time()) + 3600,
    )
    auth_time: int = Field(
        ...,
        description="認証時刻(auth_time)",
        example=int(time.time()),
    )
    status: int = Field(
        ...,
        description="トークンの状態(有効:1、無効:0)",
        example="active",
        max_length=255,
    )
