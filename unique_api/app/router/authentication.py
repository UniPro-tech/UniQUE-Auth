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

    # セッションを作成
    session = Sessions(
        user_id=validated_user.id,
        ip_address=request.client.host,  # type: ignore
        user_agent=request.headers.get("User-Agent", ""),
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),  # 1時間有効
        is_enable=True,
    )
    db.add(session)
    db.commit()

    response = {
        "message": "Authentication successful",
        "session_id": session.id,
    }

    return response
