from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import hashlib

from unique_api.app.db import get_db
from unique_api.app.model import AccessTokens, Users
from unique_api.app.services.token.hash import make_token_hasher
from unique_api.app.config import settings
from unique_api.app.schemas.errors import create_token_error_response

router = APIRouter()


def _bearer_token_from_request(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1]


@router.get("/userinfo")
@router.post("/userinfo")
async def userinfo(request: Request, db: Session = Depends(get_db)):
    """
    OpenID Connect UserInfo endpoint.
    Authorization: Bearer <access_token> を想定。
    """
    token = _bearer_token_from_request(request)
    if not token:
        return create_token_error_response(
            error="invalid_request",
            error_description="Missing Authorization Bearer token",
            status_code=401,
            www_authenticate="Bearer",
        )

    # トークンの署名検証（公開鍵/HMAC を使う）
    try:
        hash_maker = make_token_hasher(
            algorithm=settings.JWT_ALGORITHM,
            private_key_path=settings.RSA_PRIVATE_KEY_PATH,
            public_key_path=settings.RSA_PUBLIC_KEY_PATH,
            secret_key=getattr(settings, "HMAC_SECRET", None),
        )
        # verify は例外を投げる可能性があるが、audience は未指定（任意）
        hash_maker.verify(token)
    except Exception:
        return create_token_error_response(
            error="invalid_token",
            error_description="Invalid access token",
            status_code=401,
            www_authenticate='Bearer error="invalid_token"',
        )

    # DB に保存されているハッシュでトークンを探す
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    at = db.query(AccessTokens).filter_by(hash=token_hash).first()
    if not at or at.revoked:
        return create_token_error_response(
            error="invalid_token",
            error_description="Token revoked or not found",
            status_code=401,
            www_authenticate='Bearer error="invalid_token"',
        )

    # 有効期限チェック
    now = datetime.now(timezone.utc)
    exp = at.exp
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if now > exp:
        return create_token_error_response(
            error="invalid_token",
            error_description="Token expired",
            status_code=401,
            www_authenticate='Bearer error="invalid_token"',
        )

    # ユーザ情報を返す
    user = db.query(Users).filter_by(id=at.user_id).first()
    if not user:
        return create_token_error_response(
            error="invalid_token",
            error_description="Associated user not found",
            status_code=401,
            www_authenticate='Bearer error="invalid_token"',
        )

    scopes = (at.scope or "").split()
    claims: dict = {"sub": user.id}
    if "email" in scopes:
        claims.update({"email": user.email, "email_verified": bool(user.email)})
    if "profile" in scopes:
        # profile クレームは可能な限り埋める
        claims.update(
            {
                "name": user.name or user.custom_id,
                "preferred_username": user.custom_id or user.name,
            }
        )
    # openid スコープがあれば sub は必須なので既に含めている

    return JSONResponse(
        content=claims, headers={"Cache-Control": "no-store", "Pragma": "no-cache"}
    )
