from typing import List
import time
from pydantic import BaseModel, Field
from nanoid import generate


class BaseToken(BaseModel):
    """
    UniQUEのトークンの基底クラス
    Args:
        <alg> <str>:
                暗号化アルゴリズム(UniQUEではHS256のみ)
        <typ> <str>:
                トークンの種類(UniQUEではJWTのみ)
        <iss> <str>:
                発行者(UniQUEではhttps://portal.uniproject-tech.net)
        <jti> <int>:
                トークンID
        <sub> <int>:
                クライアントアプリケーションID
        <for_> <int>:
                クライアントユーザーID
    """
    alg: str = Field(default="HS256")
    typ: str = Field(default="JWT")
    iss: str = Field(default="https://portal.uniproject-tech.net")
    jti: int = Field(default=generate(), description="TokenID")
    sub: int = Field(..., description="ClientAppID")
    for_: int = Field(..., description="ClientUserID")


class AccessToken(BaseToken):
    """
    AccessTokenのスキーマ
    Args:
        <scope> <List[str]>:
                パーミッション
        <exp> <int>:
                有効期限(AccessTokenは7日間)
    """
    scope: List[str] = Field(..., description="permissions")
    exp: int = Field(default=time.time() + 604800, description="有効期限")

    class Config:
        orm_mode = True


class RefreshToken(BaseToken):
    """
    RefreshTokenのスキーマ
    Args:
        <exp> <int>:
                有効期限(RefreshTokenは14日間)
    """
    exp: int = Field(default=time.time() + 1209600, description="有効期限")

    class Config:
        orm_mode = True
