from datetime import datetime, timedelta, timezone
import hashlib
import base64
import jwt
from dataclasses import dataclass
from typing import Optional, Union, List, TYPE_CHECKING
from unique_api.app.config import settings
from typing_extensions import deprecated
from abc import ABC, abstractmethod
from unique_api.app.main import hash_maker

if TYPE_CHECKING:
    from unique_api.app.services.token.hash import TokenHashBase


@deprecated("削除予定です。make_token_hasher を使用してください。")
def generate_at_hash(access_token: str, algorithm: str = "HS256") -> str:
    """Generate at_hash claim value as per OIDC spec"""
    hash_func = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512,
        "RS256": hashlib.sha256,
        "RS384": hashlib.sha384,
        "RS512": hashlib.sha512,
    }.get(algorithm, hashlib.sha256)
    token_hash = hash_func(access_token.encode()).digest()
    half_hash = token_hash[: len(token_hash) // 2]
    at_hash = base64.urlsafe_b64encode(half_hash).decode().rstrip("=")
    return at_hash


def create_id_token(
    sub: str,
    aud: Union[str, List[str]],
    auth_time: int,
    nonce: Optional[str] = None,
    acr: Optional[str] = None,
    amr: Optional[str] = None,
    at_hash: Optional[str] = None,
    azp: Optional[str] = None,
) -> str:
    """
    Create an ID Token as per OpenID Connect spec

    Parameters:
    - sub: Subject Identifier
    - aud: Audience(s)
    - auth_time: Time when the authentication occurred
    - nonce: String value used to associate a Client session with an ID Token
    - acr: Authentication Context Class Reference
    - amr: Authentication Methods References
    - at_hash: Access Token hash value
    - azp: Authorized party (required when the ID Token has a single audience value and that audience is different from the authorized party)
    """
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(minutes=settings.ID_TOKEN_EXPIRE_MINUTES)

    claims = {
        "iss": settings.ISSUER,  # REQUIRED. Issuer Identifier
        "sub": sub,  # REQUIRED. Subject Identifier
        "aud": aud,  # REQUIRED. Audience(s)
        # REQUIRED. Expiration time
        "exp": int((now + expires_delta).timestamp()),
        # REQUIRED. Time at which the JWT was issued
        "iat": int(now.timestamp()),
        "auth_time": auth_time,  # Time when the authentication occurred
    }

    if nonce is not None:
        claims["nonce"] = nonce

    if acr is not None:
        claims["acr"] = acr

    if amr is not None:
        claims["amr"] = amr

    if at_hash is not None:
        claims["at_hash"] = at_hash

    # Add azp if multiple audiences
    if isinstance(aud, list) and len(aud) > 1 and azp is not None:
        claims["azp"] = azp

    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    sub: str,
    client_id: str,
    scope: str,
    aud: Union[str, List[str]],
) -> str:
    """
    Create an Access Token
    """
    now = datetime.utcnow()
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    claims = {
        "iss": settings.ISSUER,
        "sub": sub,
        "aud": aud,
        "scope": scope,
        "exp": int((now + expires_delta).timestamp()),
        "iat": int(now.timestamp()),
    }

    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    sub: str,
    client_id: str,
) -> str:
    """
    Create a Refresh Token
    """
    now = datetime.utcnow()
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    claims = {
        "iss": settings.ISSUER,
        "sub": sub,
        "aud": client_id,
        "exp": int((now + expires_delta).timestamp()),
        "iat": int(now.timestamp()),
    }

    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class TokenBase(ABC):
    """
    Tokenbaseの基底クラス
    Token操作の共通インターフェースを定義
    - tokentype: トークンタイプを返す抽象プロパティ
    - generate_token: トークンを生成する抽象メソッド
    - token_validate: トークンを検証する抽象メソッド
    """

    @property
    @abstractmethod
    def tokentype(self) -> str:
        """トークンタイプを返す抽象プロパティ"""
        pass

    @abstractmethod
    def generate_token(self) -> str:
        """トークンを生成する抽象メソッド"""
        pass

    @abstractmethod
    def token_validate(self, token: str) -> bool:
        """トークンを検証する抽象メソッド"""
        pass


class AccessToken(TokenBase):
    def __init__(self, iss: str, sub: str, client_id: str, scope: str, aud: Union[str, List[str]], exp: int, iat: int, jti: str, hash_maker: TokenHashBase):
        self.iss = iss
        self.sub = sub
        self.client_id = client_id
        self.scope = scope
        self.aud = aud
        self.exp = exp
        self.iat = iat
        self.jti = jti
        self.auth_time = iat
        self.amr = ["pwd"]
        self.hash_maker = hash_maker

    @property
    def tokentype(self) -> str:
        return self._alg

    def generate_token(self) -> str:
        hash_maker.sign(
            payload={
                "iss": self.iss,
                "sub": self.sub,
                "aud": self.aud,
                "exp": self.exp,
                "jti": self.jti,
                "iat": self.iat,
                "scope": self.scope,
                "client_id": self.client_id,
                "auth_time": self.auth_time,
                "amr": self.amr,
            },
            header={
                "typ": "JWT",
                "alg": self.hash_maker.algorithm
            }
        )

    def token_validate(self, token: str) -> bool:
        try:
            decoded = hash_maker.verify(token, audience=self.aud)
            return decoded["sub"] == self.sub and decoded["scope"] == self.scope
        except jwt.PyJWTError:
            return False


class RefreshToken(TokenBase):
    def __init__(self, iss: str, sub: str, client_id: str, aud: str, exp: int, iat: int, scope: dict, jti: str, hash_maker: TokenHashBase):
        self.iss = iss
        self.sub = sub
        self.client_id = client_id
        self.aud = aud
        self.exp = exp
        self.iat = iat
        self.jti = jti
        self.scope = scope
        self.auth_time = iat
        self.hash_maker = hash_maker

    @property
    def tokentype(self) -> str:
        return self.hash_maker.algorithm

    def generate_token(self) -> str:
        hash_maker.sign(
            payload={
                "iss": self.iss,
                "sub": self.sub,
                "aud": self.aud,
                "exp": self.exp,
                "iat": self.iat,
                "jti": self.jti,
                "scope": self.scope,
                "client_id": self.client_id,
                "auth_time": self.auth_time,
            },
            header={
                "typ": "JWT",
                "alg": self.hash_maker.algorithm
            }
        )

    def token_validate(self, token: str) -> bool:
        try:
            decoded = hash_maker.verify(token, audience=self.aud)
            return decoded["sub"] == self.sub
        except jwt.PyJWTError:
            return False


class IDToken(TokenBase):
    def __init__(self, iss: str, sub: str, aud: Union[str, List[str]], exp: int, iat: int, auth_time: int, nonce: Optional[str], acr: Optional[str], amr: Optional[List[str]], at_hash: Optional[str], azp: Optional[str], hash_maker: TokenHashBase):
        self.iss = iss
        self.sub = sub
        self.aud = aud
        self.exp = exp
        self.iat = iat
        self.auth_time = auth_time
        self.nonce = nonce
        self.acr = acr
        self.amr = amr
        self.at_hash = at_hash
        self.azp = azp
        self.hash_maker = hash_maker

    @property
    def tokentype(self) -> str:
        return self.hash_maker.algorithm

    def generate_token(self) -> str:
        payload = {
            "iss": self.iss,
            "sub": self.sub,
            "aud": self.aud,
            "exp": self.exp,
            "iat": self.iat,
            "auth_time": self.auth_time,
        }
        if self.nonce:
            payload["nonce"] = self.nonce
        if self.acr:
            payload["acr"] = self.acr
        if self.amr:
            payload["amr"] = self.amr
        if self.at_hash:
            payload["at_hash"] = self.at_hash
        if isinstance(self.aud, list) and len(self.aud) > 1 and self.azp:
            payload["azp"] = self.azp

        return hash_maker.sign(
            payload=payload,
            header={
                "typ": "JWT",
                "alg": self.hash_maker.algorithm
            }
        )

    def token_validate(self, token: str) -> bool:
        try:
            decoded = hash_maker.verify(token, audience=self.aud)
            return decoded["sub"] == self.sub
        except jwt.PyJWTError:
            return False


@dataclass
class TokenData:
    """
    トークンデータオブジェクト
    sub:
        ユーザーID
    client_id:
        クライアントID(audと同じで良い)
    scope:
        スコープ文字列
    aud:
        トークンの受信者(クライアントIDまたはリソースサーバーID)
    exp:
        有効期限(UNIXタイムスタンプ)
    iat:
        発行時間(UNIXタイムスタンプ)
    jti:
        トークンID(一意な識別子)
    iss:
        発行者
    amr:
        認証方法参照リスト
    nonce:
        ノンス値
    acr:
        認証コンテキストクラス参照
    azp:
        認可された当事者
    at_hash:
        アクセストークンハッシュ値
    """
    sub: str
    client_id: str
    scope: str
    aud: Union[str, List[str]]
    exp: int
    iat: int
    jti: str = None
    iss: str = None
    amr: List[str] = None
    nance: str = None
    acr: str = None
    azp: str = None
    at_hash: str = None


def token_maker(
    hash_maker: TokenHashBase,
    token_type: str,
    token_data: TokenData,
) -> TokenBase:
    """
    トークン生成オブジェクトを返すファクトリ関数
    hash_maker:
        トークンハッシュ化オブジェクト
    token_type:
        'access_token' または 'refresh_token' または 'id_token'
    token_data:
        トークンデータオブジェクト
    """
    if token_type == "access_token":
        return AccessToken(
            iss=token_data.iss,
            sub=token_data.sub,
            client_id=token_data.client_id,
            scope=token_data.scope,
            aud=token_data.aud,
            exp=token_data.exp,
            iat=token_data.iat,
            jti=token_data.jti,
            hash_maker=hash_maker,
        )
    elif token_type == "refresh_token":
        return RefreshToken(
            iss=token_data.iss,
            sub=token_data.sub,
            client_id=token_data.client_id,
            aud=token_data.aud,
            exp=token_data.exp,
            iat=token_data.iat,
            scope=token_data.scope,
            jti=token_data.jti,
            hash_maker=hash_maker,
        )
    elif token_type == "id_token":
        return IDToken(
            iss=token_data.iss,
            sub=token_data.sub,
            aud=token_data.aud,
            exp=token_data.exp,
            iat=token_data.iat,
            auth_time=token_data.iat,
            nonce=token_data.nance,
            acr=token_data.acr,
            amr=token_data.amr,
            at_hash=token_data.at_hash,
            azp=token_data.azp,
            hash_maker=hash_maker,
        )
    else:
        raise ValueError(f"Unsupported token type: {token_type}")
