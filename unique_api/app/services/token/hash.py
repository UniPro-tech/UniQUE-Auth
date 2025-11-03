import hashlib
import os
import jwt
import hmac
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from unique_api.app.config import settings


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
            raise ValueError(
                "HMACTokenHash only supports HMAC algorithms (HS256, HS384, HS512)"
            )
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
        return jwt.decode(
            token, self.secret_key, algorithms=[self._alg], audience=audience
        )

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

    def __init__(
        self,
        private_key: Optional[str],
        public_key: Optional[str],
        algorithm: str = "RS256",
    ):
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
        return jwt.decode(
            token, self.public_key, algorithms=[self._alg], audience=audience
        )


# ---------------- ファクトリ ----------------
def make_token_hasher(
    algorithm: str,
    secret_key: Optional[str] = None,
    private_key_path: Optional[str] = settings.RSA_PRIVATE_KEY_PATH,
    public_key_path: Optional[str] = settings.RSA_PUBLIC_KEY_PATH,
) -> TokenHashBase:
    """
    指定したアルゴリズムに応じたトークンハッシュ化オブジェクトを生成するファクトリ関数
    """
    if algorithm.startswith("HS"):
        if not secret_key:
            raise ValueError("secret_key required for HS*")
        return HMACTokenHash(secret_key=secret_key, algorithm=algorithm)
    if algorithm.startswith(("RS", "PS", "ES", "Ed")):
        if not (private_key_path and public_key_path):
            raise ValueError("private_key and public_key required for RSA/ECDSA/EdDSA")
        return RSATokenHash(private_key=private_key_path, public_key=public_key_path, algorithm=algorithm)
    raise ValueError("Unsupported algorithm")
