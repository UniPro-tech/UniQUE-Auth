from fastapi import HTTPException
from sqlalchemy.orm import Session
from unique_api.app.model.app import Apps
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


def verify_client_secret(db: Session, authorization: str | None) -> tuple[bool, Apps | None]:
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
        app = db.query(Apps).filter_by(client_id=client_id).first()
        return (
            client_id == app.client_id and client_secret == app.client_secret,
            app
        )
    except (ValueError, IndexError):
        return False, None
