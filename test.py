import os
import hashlib
import jwt
import hmac
from typing import Optional, Union, List, Dict, Any
from abc import ABC, abstractmethod
from time import time
from dataclasses import dataclass


class TokenHashBase(ABC):
    """トークンのハッシュ化復号化を行うための抽象基底クラス"""
    @property
    @abstractmethod
    def algorithm(self) -> str:
        pass

    @abstractmethod
    def sign(self, payload: Dict[str, Any]) -> str:
        """署名してトークン(JWT等)を返す"""
        pass

    @abstractmethod
    def verify(self, token: str, *, audience: Optional[str] = None) -> Dict[str, Any]:
        """検証してデコード済みクレームを返す（失敗時は例外を投げる）"""
        pass


# ---------------- HMAC 実装 ----------------
class HMACTokenHash(TokenHashBase):
    """HMACベースのトークンハッシュ化クラス"""
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        if not algorithm.startswith("HS"):
            raise ValueError("HMACTokenHash only supports HMAC algorithms (HS256, HS384, HS512)")
        self.secret_key = secret_key
        self._alg = algorithm

    @property
    def algorithm(self) -> str:
        return self._alg

    def sign(self, payload: Dict[str, Any]) -> str:
        # JWT 形式で返す（必要でなければ別メソッドで生の MAC を返す）
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify(self, token: str, *, audience: Optional[str] = None) -> Dict[str, Any]:
        # jwt.decode が署名・exp 等を検証してデコード済み claims を返す
        return jwt.decode(token, self.secret_key, algorithms=[self._alg], audience=audience)

    # 生の HMAC を欲しい場合
    def mac_hex(self, data: str) -> str:
        # digestmod をアルゴリズムに応じて選択
        digest = {
            "HS256": hashlib.sha256,
            "HS384": hashlib.sha384,
            "HS512": hashlib.sha512,
        }.get(self._alg, hashlib.sha256)
        return hmac.new(self.secret_key.encode(), data.encode(), digest).hexdigest()


# ---------------- RSA 実装 ----------------
class RSATokenHash(TokenHashBase):
    """RSAベースのトークンハッシュ化クラス"""
    def __init__(self, private_key: Optional[str], public_key: Optional[str], algorithm: str = "RS256"):
        def _load_if_path(k: Optional[str]) -> Optional[str]:
            if k is None:
                return None
            # 文字列がファイルとして存在するなら中身を読み込む
            if os.path.exists(k) and os.path.isfile(k):
                with open(k, "rb") as f:
                    return f.read().decode()  # PEM を文字列で返す
            return k  # そのまま PEM 文字列だと仮定
        self.private_key = _load_if_path(private_key)
        self.public_key = _load_if_path(public_key)
        self._alg = algorithm

    @property
    def algorithm(self) -> str:
        return self._alg

    def sign(self, payload: Dict[str, Any]) -> str:
        if not self.private_key:
            raise ValueError("private_key is required for signing")
        return jwt.encode(payload, self.private_key, algorithm=self._alg)

    def verify(self, token: str, *, audience: Optional[str] = None) -> Dict[str, Any]:
        if not self.public_key:
            raise ValueError("public_key is required for verification")
        return jwt.decode(token, self.public_key, algorithms=[self._alg], audience=audience)


# ---------------- ファクトリ ----------------
def make_token_hasher(
    algorithm: str,
    secret_key: Optional[str] = None,
    private_key: Optional[str] = None,
    public_key: Optional[str] = None,
) -> TokenHashBase:
    """
    指定したアルゴリズムに応じたトークンハッシュ化オブジェクトを生成するファクトリ関数
    """
    if algorithm.startswith("HS"):
        if not secret_key:
            raise ValueError("secret_key required for HS*")
        return HMACTokenHash(secret_key=secret_key, algorithm=algorithm)
    if algorithm.startswith(("RS", "PS", "ES", "Ed")):
        if not (private_key and public_key):
            raise ValueError("private_key and public_key required for RSA/ECDSA/EdDSA")
        return RSATokenHash(private_key=private_key, public_key=public_key, algorithm=algorithm)
    raise ValueError("Unsupported algorithm")


h = make_token_hasher("HS256", secret_key="71c8f68bb6bbf6254b920b9622ab7df535d0d190599fea213d272a23bbb0c81e")
token = h.sign({"sub": "user1", "iat": time(), "exp": time() + 3600})
claims = h.verify(token)
print(claims)

rsa_priv_pem_path = "/home/sibainu/Project/UniQUE-Auth/rsa_private.pem"
rsa_pub_pem_path = "/home/sibainu/Project/UniQUE-Auth/rsa_public.pem"

hash_maker = make_token_hasher("RS256", private_key=rsa_priv_pem_path, public_key=rsa_pub_pem_path)
r_tok = hash_maker.sign({"sub": "user2", "iat": time(), "exp": time() + 3600})
claims_r = hash_maker.verify(r_tok)
print(claims_r)


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


token_make = token_maker(
    hash_maker=hash_maker,
    token_type="access_token",
    token_payload=TokenPayload(
        sub="user1",
        client_id="client123",
        scope="read write",
        aud="client123",
        exp=int(time()) + 3600,
        iat=int(time()),
        jti="unique-token-id-123",
        iss="https://example.com",
    )
)
token_str = token_make.generate_token()
print("Generated Token:", token_str)
is_valid = token_make.token_validate(token_str)
print("Is Token Valid?", is_valid)
