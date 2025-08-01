from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from db import get_db
import hashlib
import os
from unique_api.app.model import (
    Users,
    Sessions
)

router = APIRouter()
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "../pages")
)


@router.get("/login")
async def login(request: Request):
    """
    OIDC 認可フロー開始時、外部クライアントから
    リクエストパラメータを検証して request.session に保存した上で
    このエンドポイントにリダイレクトさせる想定です。
    GET では単にログインフォームを表示。
    """
    action_url = "login"
    if request.query_params:
        action_url += f"?{urlencode(request.query_params)}"
    return templates.TemplateResponse(
        "login.html", {"request": request, "action_url": action_url}
    )


@router.post("/login")
async def login_post(
    request: Request,
    custom_id: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    ログインフォームの POST 送信を受けて、認証処理を行う。
    認証成功時はセッションにユーザ情報を保存し、リダイレクトする。
    """
    print("Login POST request received:", dict(request.query_params))
    request_query_params = dict(request.query_params)
    # ここでユーザ認証を行う
    # 例えば、email と password を使ってユーザを検索し、認証が成功したら
    # セッションにユーザ情報を保存する
    validated_user = (
        db.query(Users)
        .filter_by(
            custom_id=custom_id,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
        )
        .first()
    )

    if validated_user is None:
        # 認証失敗
        response = HTTPException(status_code=401, detail="Invalid username or password")
        return response

    # response_typeがサポートされているcodeか確認
    response_type = request_query_params.get("response_type")
    if type(response_type) is str:
        redirect_url = "auth?" + urlencode(dict(request.query_params))
    else:
        # OIDC認証ではない通常の認証であればルートページに飛ばす
        redirect_url = "/"

    # セッションを作成
    session = Sessions(
        user_id=validated_user.id,
        ip_address=request.client.host,  # type: ignore
        user_agent=request.headers.get("User-Agent", ""),
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),  # 1時間有効
        is_enable=True
    )
    db.add(session)
    db.commit()
    # リダイレクト
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(key="session_", value=session.id)
    return response


@router.get("/logout")
async def logout(request: Request):
    """
    ログアウト処理を行うエンドポイント。
    """
    request.session.clear()
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="session_")
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
        return templates.TemplateResponse(
            "signup.html", {"request": request, "error": "Member is not registered"}
        )

    # ユーザ名の重複チェック
    existing_user = db.query(Users).filter_by(custom_id=custom_id).first()
    if existing_user:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "error": "User already exists"}
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
        return templates.TemplateResponse(
            "signup.html", {"request": request, "error": "User already exists"}
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
