"""認証関連のルーターを定義するモジュール"""

import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from unique_api.app.db import get_db
from unique_api.app.model import Users, Sessions
from unique_api.app.schemas.authentication import AuthenticationRequest

router = APIRouter()


@router.post("/authentication")
async def authentication_post(
    request: AuthenticationRequest,
    db: Session = Depends(get_db),
):
    """
    ログインフォームのPOST送信を受けて、認証処理を行う
    - ユーザー認証
    - セッション作成
    - プロンプトパラメータの処理
    - max_ageパラメータの処理
    """

    custom_id = request.username
    password = request.password
    ip = request.ip
    user_agent = request.user_agent

    # ユーザー認証
    validated_user = (
        db.query(Users)
        .filter_by(
            custom_id=custom_id,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
        )
        .first()
    )

    if validated_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if request.remember_me and request.max_age is None:
        request.max_age = 60 * 60 * 24 * 30  # 30日
    elif request.max_age is None:
        request.max_age = 60 * 60 * 24 * 7  # 7日

    # セッションを作成
    session = Sessions(
        user_id=validated_user.id,
        ip_address=ip,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=request.max_age),
        is_enable=True,
    )
    db.add(session)
    db.commit()

    response = {
        "message": "Authentication successful",
        "session_id": session.id,
    }

    return response
