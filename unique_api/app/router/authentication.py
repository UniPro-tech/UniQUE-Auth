from fastapi import APIRouter, Request, Depends, Form, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from typing import Optional
from unique_api.app.db import get_db
import hashlib
import os
import secrets
from unique_api.app.model import (
    Users,
    Sessions
)
from unique_api.app.schemas.authentication import AuthenticationRequest
from unique_api.app.schemas.login import LoginRequest
from unique_api.app.schemas.errors import (
    create_error_response,
    OAuthErrorCode
)


def get_session(request: Request, db: Session) -> Optional[Sessions]:
    """セッションを取得"""
    session_id = request.cookies.get("session_")
    if not session_id:
        return None

    session = db.query(Sessions).filter_by(id=session_id).first()
    if not session or not session.is_enable:
        return None

    return session


def handle_authentication_required(request: Request, params: AuthenticationRequest) -> RedirectResponse:
    """認証が必要な場合のハンドリング"""
    login_url = "login"
    if params:
        login_url += f"?{urlencode(params.dict(exclude_none=True))}"
    return RedirectResponse(url=login_url, status_code=302)


def needs_consent(user_id: str, client_id: str, scope: str, db: Session) -> bool:
    """同意が必要かどうかを判定"""
    # TODO: 同意の記録を確認する実装
    return True


def show_consent_screen(
    request: Request,
    session: Sessions,
    params: AuthenticationRequest,
    db: Session
):
    """同意画面を表示"""
    # TODO: 同意画面の実装
    return templates.TemplateResponse(
        "consent.html",
        {
            "request": request,
            "user": session.user,
            "client": params.client_id,
            "scope": params.scope
        }
    )


router = APIRouter()
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "../../pages")
)


@router.get("/login")
async def login(
    request: Request,
    params: AuthenticationRequest = Depends(),
    csrf_token: str = Cookie(None)
):
    """
    OIDC 認可フロー開始時のログイン画面表示
    - CSRF対策のトークンを生成
    - ログインフォームを表示
    """
    # CSRF対策トークンの生成
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        response = JSONResponse(
            content={
                "csrf_token": csrf_token,
                "action_url": f"login?{urlencode(params.dict(exclude_none=True))}",
            }
        )
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        return response

    return JSONResponse(
        content={
            "csrf_token": csrf_token,
            "action_url": f"login?{urlencode(params.dict(exclude_none=True))}",
        }
    )


@router.post("/login")
async def login_post(
    request: Request,
    login_data: LoginRequest,
    params: AuthenticationRequest = Depends(),
    db: Session = Depends(get_db),
):
    """
    ログインフォームのPOST送信を受けて、認証処理を行う
    - CSRF対策
    - ユーザー認証
    - セッション作成
    - プロンプトパラメータの処理
    - max_ageパラメータの処理
    """
    # CSRF対策
    cookie_token = request.cookies.get("csrf_token")
    if not cookie_token or cookie_token != login_data.csrf_token:
        return create_error_response(
            error=OAuthErrorCode.INVALID_REQUEST,
            error_description="CSRF token validation failed",
            state=params.state
        )

    # ユーザー認証
    validated_user = (
        db.query(Users)
        .filter_by(
            custom_id=login_data.custom_id,
            password_hash=hashlib.sha256(login_data.password.encode()).hexdigest(),
        ).first()
    )

    if validated_user is None:
        return create_error_response(
            error=OAuthErrorCode.ACCESS_DENIED,
            error_description="Invalid username or password",
            state=params.state,
            status_code=401
        )

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

    # レスポンスの準備
    redirect_url = f"auth?{urlencode(params.dict(exclude_none=True))}"
    response = JSONResponse(
        content={
            "success": True,
            "redirect_url": redirect_url,
        }
    )
    response.set_cookie(
        key="session_",
        value=session.id,
        httponly=True,
        secure=True,
        samesite="lax"
    )

    # CSRFトークンを削除
    response.delete_cookie(key="csrf_token")

    return response


@router.get("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    ログアウト処理を行うエンドポイント
    - セッションの無効化
    - Cookieの削除
    """
    # セッションを無効化
    session_id = request.cookies.get("session_")
    if session_id:
        session = db.query(Sessions).filter_by(id=session_id).first()
        if session:
            session.is_enable = False
            db.add(session)
            db.commit()

    # レスポンスの準備
    response = JSONResponse(
        content={
            "success": True,
            "message": "Logged out successfully"
        }
    )
    response.delete_cookie(key="session_")
    response.delete_cookie(key="csrf_token")

    return response


@router.get("/signup")
async def signup(request: Request):
    """
    サインアップ処理を行うエンドポイント。
    """
    action_url = "/signup"
    if request.query_params:
        action_url += f"?{urlencode(request.query_params)}"
    return templates.TemplateResponse(
        "signup.html", {"request": request, "action_url": action_url}
    )


@router.post("/signup")
async def signup_post(
    request: Request,
    custom_id: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    サインアップフォームの POST 送信を受けて、ユーザ登録処理を行う。
    登録成功時はログインページにリダイレクトする。
    """
    print("Signup POST request received:", dict(request.query_params))

    # ユーザ名のメンバーの登録可否
    existing_member = db.query(Users).filter_by(custom_id=custom_id).first()
    if not existing_member:
        return create_error_response(
            error=OAuthErrorCode.INVALID_REQUEST,
            error_description="Member is not registered",
            status_code=400
        )

    # ユーザ名の重複チェック
    existing_user = db.query(Users).filter_by(custom_id=custom_id).first()
    if existing_user:
        return create_error_response(
            error=OAuthErrorCode.INVALID_REQUEST,
            error_description="User already exists",
            status_code=400
        )

    # 新規ユーザの作成
    new_user = Users(
        custom_id=custom_id,
        is_enable=True,
        password_hash=hashlib.sha256(password.encode()).hexdigest(),
        email=existing_member.email,
    )
    db.add(new_user)
    db.commit()

    # 登録成功後はログインページにリダイレクト
    return RedirectResponse(url="/login", status_code=302)


# TODO: これはFrontで実装する
@router.get("/join")
async def join(request: Request):
    """
    サインアップ処理を行うエンドポイント。
    """
    action_url = "/join"
    if request.query_params:
        action_url += f"?{urlencode(request.query_params)}"
    return templates.TemplateResponse(
        "join.html", {"request": request, "action_url": action_url}
    )


@router.post("/join")
async def join_post(
    request: Request,
    custom_id: str = Form(...),
    email: str = Form(...),
    name: str = Form(...),
    external_email: str = Form(...),
    period: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    サインアップフォームの POST 送信を受けて、ユーザ仮登録処理を行う。
    登録成功時はメールを送信する。
    """
    print("Signup POST request received:", dict(request.query_params))

    # ユーザ名の重複チェック
    existing_member = db.query(Users).filter_by(custom_id=custom_id).first()
    if existing_member:
        return create_error_response(
            error=OAuthErrorCode.INVALID_REQUEST,
            error_description="User already exists",
            status_code=400
        )

    # 新規ユーザの作成
    new_member = Users(
        custom_id=custom_id,
        name=name,
        email=email,
        external_email=external_email,
        updated_at=datetime.now(),
        joined_at=datetime.now(),
        is_enable=True,
        period=period,
        system=False,
    )
    db.add(new_member)
    db.commit()

    # 登録成功後はログインページにリダイレクト
    return RedirectResponse(url="/login", status_code=302)
