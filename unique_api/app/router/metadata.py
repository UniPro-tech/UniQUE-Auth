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
        "authorization_endpoint": f"{settings.ISSUER}/auth",
        "token_endpoint": f"{settings.ISSUER}/token",
        "jwks_uri": f"{settings.ISSUER}/.well-known/jwks.json",
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
