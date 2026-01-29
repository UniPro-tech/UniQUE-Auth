import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..config import settings
from ..services.client_auth import ClientAuthMethod

router = APIRouter()


@router.get("/.well-known/openid-configuration")
async def openid_configuration():
    """
    OpenID Connect Discovery 1.0のメタデータエンドポイント
    https://openid.net/specs/openid-connect-discovery-1_0.html
    """
    metadata = {
        "issuer": settings.ISSUER,
        "authorization_endpoint": f"{settings.FRONTEND_URL}/auth",
        "token_endpoint": f"{settings.ISSUER}/token",
        "jwks_uri": f"{settings.ISSUER}/.well-known/jwks.json",
        "userinfo_endpoint": f"{settings.ISSUER}/userinfo",
        "scopes_supported": ["openid", "profile", "email"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": [settings.JWT_ALGORITHM],
        "token_endpoint_auth_methods_supported": [
            ClientAuthMethod.CLIENT_SECRET_BASIC,
            ClientAuthMethod.CLIENT_SECRET_POST,
        ],
        "claims_supported": [
            "email",
            "email_verified",
            "name",
            "preferred_username",
            "iss",
            "sub",
            "aud",
            "exp",
            "iat",
            "auth_time",
            "nonce",
            "acr",
            "amr",
            "azp",
            "at_hash",
        ],
        "code_challenge_methods_supported": ["plain", "S256"],
    }

    return JSONResponse(
        content=metadata,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Type": "application/json",
        },
    )


@router.get("/.well-known/jwks.json")
async def jwks():
    """
    JSON Web Key Set (JWKS) エンドポイント
    https://openid.net/specs/openid-connect-discovery-1_0.html#JWKSEndpoint
    """
    jwks_data = {"keys": _generate_jwks_from_public_key()}  # 公開鍵からJWKSを生成

    return JSONResponse(
        content=jwks_data,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Type": "application/json",
        },
    )


def _generate_jwks_from_public_key() -> list:
    """
    公開鍵ファイルからJWKSを生成する
    """
    if not settings.RSA_PUBLIC_KEY_PATH:
        return []

    try:
        # 公開鍵を読み込む
        with open(settings.RSA_PUBLIC_KEY_PATH, "rb") as f:
            public_key_data = f.read()

        # 公開鍵をロード
        public_key = serialization.load_pem_public_key(public_key_data)

        # RSA公開鍵の場合のみ処理
        if isinstance(public_key, rsa.RSAPublicKey):
            public_numbers = public_key.public_numbers()

            # nとeをBase64url形式に変換
            def int_to_base64url(num: int) -> str:
                num_bytes = num.to_bytes((num.bit_length() + 7) // 8, byteorder="big")
                return base64.urlsafe_b64encode(num_bytes).decode("utf-8").rstrip("=")

            n = int_to_base64url(public_numbers.n)
            e = int_to_base64url(public_numbers.e)

            # JWKを構築
            jwk = {
                "kty": "RSA",
                "use": "sig",
                "alg": settings.JWT_ALGORITHM,
                "n": n,
                "e": e,
            }

            # kid（Key ID）を生成（オプション）
            # 公開鍵の指紋をsha256ハッシュで生成
            import hashlib

            key_id = hashlib.sha256(public_key_data).hexdigest()[:16]
            jwk["kid"] = key_id

            return [jwk]
        else:
            # RSA以外の鍵タイプには対応していない
            return []

    except (FileNotFoundError, ValueError, IOError) as e:
        # エラーログを出力するべきだが、ここでは空のリストを返す
        print(f"Error generating JWKS: {e}")
        return []
