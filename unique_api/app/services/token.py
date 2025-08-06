from datetime import datetime, timezone, timedelta
import hashlib
import base64
import jwt
from typing import Optional, Union, List
from unique_api.app.config import settings


def generate_at_hash(access_token: str, algorithm: str = settings.JWT_ALGORITHM) -> str:
    """Generate at_hash claim value as per OIDC spec"""
    hash_func = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512,
    }.get(algorithm, hashlib.sha256)

    token_hash = hash_func(access_token.encode()).digest()
    half_hash = token_hash[:len(token_hash) // 2]
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
        "sub": sub,              # REQUIRED. Subject Identifier
        "aud": aud,              # REQUIRED. Audience(s)
        "exp": int((now + expires_delta).timestamp()),  # REQUIRED. Expiration time
        "iat": int(now.timestamp()),                    # REQUIRED. Time at which the JWT was issued
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

    return jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


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
        "client_id": client_id,
        "scope": scope,
        "exp": int((now + expires_delta).timestamp()),
        "iat": int(now.timestamp())
    }

    return jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    sub: str,
    client_id: str,
    aud: Union[str, List[str]],
) -> str:
    """
    Create a Refresh Token
    """
    now = datetime.utcnow()
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    claims = {
        "iss": settings.ISSUER,
        "sub": sub,
        "aud": aud,
        "client_id": client_id,
        "exp": int((now + expires_delta).timestamp()),
        "iat": int(now.timestamp())
    }

    return jwt.encode(
        claims,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
