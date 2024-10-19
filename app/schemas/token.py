import time
from pydantic import BaseModel, Field


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
    jti: int = Field(..., description="TokenID")

    iat: int = Field(default=int(time.time()), description="発行日時")


class AccessToken(BaseToken):
    """
    AccessTokenのスキーマ
    Args:
        <scope> <List[str]>:
                パーミッション
        <exp> <int>:
                有効期限(AccessTokenは7日間)
    """
    sub: int = Field(..., description="ClientUserID")
    for_: int = Field(..., description="UserID")
    scope: int = Field(description="permissions")
    exp: int = Field(default=time.time() + 604800, description="有効期限")
    is_geted: bool = Field(default=False, description="取得済みかどうか")

    class Config:
        model_validate = True


class RefreshToken(BaseToken):
    """
    RefreshTokenのスキーマ
    Args:
        <exp> <int>:
                有効期限(RefreshTokenは14日間)
    """
    exp: int = Field(default=time.time() + 1209600, description="有効期限")

    class Config:
        model_validate = True


class DBToken(BaseModel):
    """
    DBに保存されているTokenのスキーマ
    Args:
        <client_id> <int>:
                クライアントアプリケーションID
        <user_id> <int>:
                クライアントユーザーID
        <scope> <List[str]>:
                パーミッション
        <refresh_token> <str>:
                リフレッシュトークン
    """
    acsess_token_id: str = Field(..., description="AccessToken")
    refresh_token_id: str = Field(..., description="RefreshToken")
    user_id: int = Field(..., description="ClientUserID")
    client_id: int = Field(..., description="ClientID")
    scope: int = Field(..., description="permissions")
    is_enabled: bool = Field(default=True, description="有効かどうか")

    class Config:
        model_validate = True
