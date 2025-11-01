from datetime import datetime, timezone
import jwt
import base64
import hashlib
from typing import Dict, Any, Optional
from unique_api.app.config import settings


def create_test_client_credentials(client_id: str, client_secret: str) -> str:
    """Create Basic auth header for client credentials"""
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def decode_id_token(id_token: str) -> Dict[str, Any]:
    """Decode and validate ID Token"""
    return jwt.decode(
        id_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_signature": True}
    )


def validate_id_token(
    id_token: Dict[str, Any],
    expected_sub: str,
    expected_aud: str,
    expected_nonce: Optional[str] = None,
    expected_at_hash: Optional[str] = None,
) -> None:
    """Validate ID Token claims"""
    now = datetime.now(timezone.utc)

    # 必須クレームの存在チェック
    assert "iss" in id_token
    assert "sub" in id_token
    assert "aud" in id_token
    assert "exp" in id_token
    assert "iat" in id_token
    assert "auth_time" in id_token

    # 値の検証
    assert id_token["iss"] == settings.ISSUER
    assert id_token["sub"] == expected_sub
    assert id_token["aud"] == expected_aud
    assert isinstance(id_token["exp"], int)
    assert isinstance(id_token["iat"], int)
    assert isinstance(id_token["auth_time"], int)

    # 有効期限の検証
    assert datetime.fromtimestamp(id_token["exp"], timezone.utc) > now
    assert datetime.fromtimestamp(id_token["iat"], timezone.utc) <= now
    assert datetime.fromtimestamp(id_token["auth_time"], timezone.utc) <= now

    # オプショナルクレームの検証
    if expected_nonce:
        assert id_token["nonce"] == expected_nonce

    if expected_at_hash:
        assert id_token["at_hash"] == expected_at_hash


def generate_pkce_params() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge"""
    code_verifier = base64.urlsafe_b64encode(hashlib.sha256(
        b"test_verifier").digest()).decode().rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    return code_verifier, code_challenge
