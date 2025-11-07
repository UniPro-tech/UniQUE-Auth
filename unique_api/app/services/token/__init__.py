import hashlib
import base64
import jwt
from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Any, TYPE_CHECKING
from abc import ABC, abstractmethod
from unique_api.app.main import hash_maker

if TYPE_CHECKING:
    from unique_api.app.services.token.hash import TokenHashBase


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


class TokenBase(ABC):
    """
    Tokenbaseの基底クラス
    Token操作の共通インターフェースを定義
    - tokentype: トークンタイプを返す抽象プロパティ
    - generate_token: トークンを生成する抽象メソッド
    - token_validate: トークンを検証する抽象メソッド
    """
    def __init__(self, hash_maker: TokenHashBase, extra_header: Optional[Dict[str, Any]] = None):
        self.hash_maker = hash_maker
        self.extra_header = extra_header or {}

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

    def _default_headers(self) -> Dict[str, Any]:
        """デフォルトのヘッダーを返すヘルパーメソッド"""
        headers = {
            "typ": "JWT",
            "alg": getattr(self.hash_maker, "algorithm", "none"),
        }
        kid = getattr(self.hash_maker, "key", None)
        if kid:
            headers["kid"] = kid

        merged = {**headers, **(self.extra_header or {})}

        return {k: v for k, v in merged.items() if v is not None}


class AccessToken(TokenBase):
    def __init__(self, iss: str, sub: str, client_id: str, scope: str,
                 aud: Union[str, List[str]], exp: int, iat: int, jti: str,
                 hash_maker: TokenHashBase, extra_header: Optional[Dict[str, Any]] = None):
        super().__init__(hash_maker, extra_header)
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

    @property
    def tokentype(self) -> str:
        return "access_token"

    def generate_token(self) -> str:
        payload = {
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
        }
        header = self._default_headers()
        return self.hash_maker.sign(
            payload=payload,
            header=header
        )

    def token_validate(self, token: str) -> bool:
        try:
            decoded = hash_maker.verify(token, audience=self.aud)
            return decoded["sub"] == self.sub and decoded.get("scope") == self.scope
        except jwt.PyJWTError:
            return False


class RefreshToken(TokenBase):
    def __init__(self, iss: str, sub: str, client_id: str, aud: str,
                 exp: int, iat: int, scope: Union[str, Dict[str, Any]], jti: str,
                 hash_maker: TokenHashBase, extra_header: Optional[Dict[str, Any]] = None):
        super().__init__(hash_maker, extra_header)
        self.iss = iss
        self.sub = sub
        self.client_id = client_id
        self.aud = aud
        self.exp = exp
        self.iat = iat
        self.jti = jti
        self.scope = scope
        self.auth_time = iat

    @property
    def tokentype(self) -> str:
        return "refresh_token"

    def generate_token(self) -> str:
        payload = {
            "iss": self.iss,
            "sub": self.sub,
            "aud": self.aud,
            "exp": self.exp,
            "iat": self.iat,
            "jti": self.jti,
            "scope": self.scope,
            "client_id": self.client_id,
            "auth_time": self.auth_time,
        }
        header = self._default_headers()
        return self.hash_maker.sign(
            payload=payload,
            header=header
        )

    def token_validate(self, token: str) -> bool:
        try:
            decoded = hash_maker.verify(token, audience=self.aud)
            return decoded.get("sub") == self.sub and decoded.get("jti") == self.jti
        except jwt.PyJWTError:
            return False


class IDToken(TokenBase):
    def __init__(self, iss: str, sub: str, aud: Union[str, List[str]], exp: int, iat: int,
                 auth_time: int, nonce: Optional[str], acr: Optional[str], amr: Optional[List[str]],
                 at_hash: Optional[str], azp: Optional[str], hash_maker: TokenHashBase,
                 extra_header: Optional[Dict[str, Any]] = None):
        super().__init__(hash_maker, extra_header)
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

    @property
    def tokentype(self) -> str:
        return "id_token"

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

        header = self._default_headers()
        return self.hash_maker.sign(
            payload=payload,
            header=header
        )

    def token_validate(self, token: str) -> bool:
        try:
            decoded = hash_maker.verify(token, audience=self.aud)
            return decoded.get("sub") == self.sub
        except jwt.PyJWTError:
            return False


@dataclass
class TokenPayload:
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
        generate_at_hash 関数で生成可能
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


class TokenHeader:
    """
    トークンヘッダーオブジェクト
    typ:
        トークンタイプ(JWT等)
    alg:
        使用される署名アルゴリズム(HS256, RS256等)
    """
    typ: str = "JWT"
    alg: str = None


def token_maker(
    hash_maker: TokenHashBase,
    token_type: str,
    token_payload: TokenPayload,
    token_header: Optional[dict] = TokenHeader.__dict__,
) -> TokenBase:
    """
    トークン生成オブジェクトを返すファクトリ関数
    hash_maker:
        トークンハッシュ化オブジェクト
    token_type:
        'access_token' または 'refresh_token' または 'id_token'
    token_payload:
        トークンデータオブジェクト
    """
    if token_type == "access_token":
        return AccessToken(
            iss=token_payload.iss,
            sub=token_payload.sub,
            client_id=token_payload.client_id,
            scope=token_payload.scope,
            aud=token_payload.aud,
            exp=token_payload.exp,
            iat=token_payload.iat,
            jti=token_payload.jti,
            hash_maker=hash_maker,
        )
    elif token_type == "refresh_token":
        return RefreshToken(
            iss=token_payload.iss,
            sub=token_payload.sub,
            client_id=token_payload.client_id,
            aud=token_payload.aud,
            exp=token_payload.exp,
            iat=token_payload.iat,
            scope=token_payload.scope,
            jti=token_payload.jti,
            hash_maker=hash_maker,
        )
    elif token_type == "id_token":
        return IDToken(
            iss=token_payload.iss,
            sub=token_payload.sub,
            aud=token_payload.aud,
            exp=token_payload.exp,
            iat=token_payload.iat,
            auth_time=token_payload.iat,
            nonce=token_payload.nance,
            acr=token_payload.acr,
            amr=token_payload.amr,
            at_hash=token_payload.at_hash,
            azp=token_payload.azp,
            hash_maker=hash_maker,
        )
    else:
        raise ValueError(f"Unsupported token type: {token_type}")
