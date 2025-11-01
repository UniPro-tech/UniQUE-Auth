from enum import Enum
import base64
import hashlib
import hmac
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from ..model import Apps


class ClientAuthMethod(str, Enum):
    """
    OIDCプロバイダーがサポートするクライアント認証方式
    https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication
    """

    CLIENT_SECRET_BASIC = "client_secret_basic"  # HTTP Basic認証
    CLIENT_SECRET_POST = "client_secret_post"  # POSTパラメータ
    CLIENT_SECRET_JWT = "client_secret_jwt"  # 共有鍵によるJWT
    PRIVATE_KEY_JWT = "private_key_jwt"  # 秘密鍵によるJWT
    NONE = "none"  # パブリッククライアント用


def verify_client_secret_basic(
    auth_header: str,
    db: Session,
) -> Tuple[bool, Optional[Apps]]:
    """
    HTTP Basic認証によるクライアント認証を検証
    """
    if not auth_header.startswith("Basic "):
        return False, None

    try:
        # Base64デコード
        credentials = base64.b64decode(auth_header[6:]).decode()
        client_id, client_secret = credentials.split(":")

        # クライアントの検索
        app = db.query(Apps).filter_by(client_id=client_id).first()
        if not app:
            return False, None

        # シークレットの検証
        expected_hash = app.client_secret
        actual_hash = hashlib.sha256(client_secret.encode()).hexdigest()

        return hmac.compare_digest(expected_hash, actual_hash), app

    except Exception:
        return False, None


def verify_client_secret_post(
    client_id: str,
    client_secret: str,
    db: Session,
) -> Tuple[bool, Optional[Apps]]:
    """
    POSTパラメータによるクライアント認証を検証
    """
    try:
        # クライアントの検索
        app = db.query(Apps).filter_by(client_id=client_id).first()
        if not app:
            return False, None

        # シークレットの検証
        expected_hash = app.client_secret
        actual_hash = hashlib.sha256(client_secret.encode()).hexdigest()

        return hmac.compare_digest(expected_hash, actual_hash), app

    except Exception:
        return False, None
