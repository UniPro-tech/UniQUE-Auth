from fastapi import HTTPException
from typing import List
from pydantic import AnyHttpUrl
import base64


def validate_redirect_uri(
    requested_uri: AnyHttpUrl | None,
    registered_uris: List[str]
) -> str:
    if requested_uri is None:
        raise HTTPException(status_code=400, detail="Redirect URI not provided")

    if str(requested_uri) not in registered_uris:
        raise HTTPException(status_code=400, detail="Redirect URI not allowed")

    return str(requested_uri)


def token_authorization(authorization: str | None) -> tuple[str, str | None]:
    """
    クライアントシークレットを検証するメソッド。
    authorization ヘッダーが "Basic {base64エンコードされたクライアントID:クライアントシークレット}" 形式であることを確認します。
    """
    if authorization is None:
        return False

    try:
        # "Basic " プレフィックスを除去
        auth_value = authorization.split(" ")[1]
        decoded = base64.b64decode(auth_value).decode("utf-8")
        client_id, client_secret = decoded.split(":", 1)
        # クライアントIDとクライアントシークレットを比較
        return client_id, client_secret
    except (ValueError, IndexError):
        return None
