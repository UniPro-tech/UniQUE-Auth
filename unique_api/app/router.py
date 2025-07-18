from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from db import get_db
import hashlib
from uuid import uuid4
import jwt
from unique_api.app.model import (
    AccessTokens,
    RefreshTokens,
    Users,
    Sessions as UserSession,
    Apps,
    Auths,
    Consents,
    OidcAuthorizations,
    OidcTokens,
    Code,
)
import os


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

    # 認証成功
    request.session["user"] = (
        f"{{'id': {validated_user.id}, 'name': {validated_user.custom_id}}}"
    )

    if dict(request.query_params) == {}:
        redirect_url = "/"
    # OIDC 認可フローの場合、リダイレクト先の URL に
    elif dict(request.query_params).get(
        "redirect_uri"
    ):  # TODO:リダイレクト先の URI が指定されている場合
        # リダイレクト先の URL にクエリパラメータを追加
        redirect_url = "auth?" + urlencode(dict(request.query_params))

    # セッションを作成
    session = UserSession(
        user_id=validated_user.id,
        ip_address=request.client.host,  # type: ignore
        user_agent=request.headers.get("User-Agent", ""),
    )
    db.add(session)
    db.commit()
    # リダイレクト
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(key="user_id", value=validated_user.id)
    return response


@router.get("/logout")
async def logout(request: Request):
    """
    ログアウト処理を行うエンドポイント。
    """
    request.session.clear()
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="user_id")
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


@router.get("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    """
    OIDC 認可フローのためのエンドポイント。
    """
    print("Auth request received:", dict(request.query_params))
    request_query_params = dict(request.query_params)
    # セッションからユーザ情報を取得
    user_info = request.cookies.get("user_id")
    if not user_info:
        raise RedirectResponse(url="login", status_code=302)

    user = db.query(Users).filter_by(id=user_info).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    client_id = request.query_params.get("client_id")

    app = db.query(Apps).filter_by(client_id=client_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Client not found")

    # リダイレクト URI の検証
    redirect_uri = request_query_params.get("redirect_uri")
    if redirect_uri is not None:
        redirect_uris = [uri.uri for uri in app.redirect_uris]
        if redirect_uri not in redirect_uris:
            # リダイレクトURIが許可されていない場合はエラーを返す
            # TODO: RFC準拠になるように修正
            raise HTTPException(status_code=400, detail="Redirect URI not allowed")
    else:
        # リダイレクト URI が指定されていない場合はエラーを返す
        raise HTTPException(status_code=400, detail="Redirect URI not provided")

    # すでに認可されているか確認
    existing_auth = (
        db.query(Auths).filter_by(auth_user_id=user.id, app_id=app.id).first()
    )
    if existing_auth:
        # すでに認可されている場合は、scopeの権限を確認
        scopes = []
        for oidc_token in existing_auth.oidc_authorizations:
            scopes.extend(oidc_token.consent.scope.split(" "))
        if set(request_query_params["scope"].split(" ")) <= set(scopes):
            print("Existing auth found:", existing_auth.id)
            # TODO: codeを生成してリダイレクト
            pass

    # 認可されていない場合は認可画面を表示
    # リクエストパラメータをセッションストレージに署名付きで保存する
    request.session["auth_request"] = {
        "client_id": app.client_id,
        "redirect_uri": redirect_uri,
        "scope": request_query_params.get("scope", "default"),
        "state": request_query_params.get("state", str(uuid4())),
        "response_type": request_query_params.get("response_type", "code"),
    }
    action_url = "auth/confirm"
    # 認可画面に必要な情報をテンプレートに渡す
    # ここでは、アプリケーションの情報とユーザ情報を渡す
    auth_data = {
        "app": {
            "name": app.name,
            "client_id": app.client_id,
            "redirect_uris": [uri.uri for uri in app.redirect_uris],
            "scope": request_query_params.get("scope", "default"),
        },
        "user": {"name": user.custom_id, "id": user.id},
    }

    response = templates.TemplateResponse(
        "confirm.html",
        {"request": request, "action_url": action_url, "auth_data": auth_data},
    )
    return response


@router.post("/auth/confirm")
async def auth_confirm(request: Request, db: Session = Depends(get_db)):
    """
    OIDC 認可フローの確認画面での POST 送信を受けて、認可処理を行う。
    """
    print("Auth confirm request received:", dict(request.query_params))
    # セッションからリクエスト情報を取得
    auth_request = request.session.get("auth_request")
    if not auth_request:
        raise HTTPException(status_code=400, detail="No auth request found in session")
    user_info = request.cookies.get("user_id")
    if not user_info:
        raise RedirectResponse(url="login", status_code=302)

    user = db.query(Users).filter_by(id=user_info).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    app = db.query(Apps).filter_by(client_id=auth_request["client_id"]).first()
    if not app:
        raise HTTPException(status_code=404, detail="Client not found")
    # すでに認可されているか確認
    existing_auth = (
        db.query(Auths).filter_by(auth_user_id=user.id, app_id=app.id).first()
    )
    if existing_auth is None:
        # 新規認可を作成
        existing_auth = Auths(auth_user_id=user.id, app_id=app.id)
        db.add(existing_auth)
        db.flush()
    # consentテーブルを作成
    consent = Consents(scope=auth_request["scope"], is_enable=True)
    code = Code(
        token=str(uuid4()),
        exp=datetime.now(timezone.utc) + timedelta(minutes=10),
        is_enable=True,
    )
    oidc_auth = OidcAuthorizations(auth_id=existing_auth.id, code=code, consent=consent)

    db.add_all([consent, code, oidc_auth])
    db.commit()

    request.session.clear()
    print(f"http://localhost:8000/code?code={code.token}")
    return RedirectResponse(
        url=f"{auth_request['redirect_uri']}?code={code.token}",
        status_code=302,
    )


@router.get("/code")
async def get_code(request: Request, db: Session = Depends(get_db)):
    """
    OIDC 認可コードを取得するエンドポイント。
    """
    print("Get code request received:", dict(request.query_params))
    user_info = request.cookies.get("user_id")
    if not user_info:
        raise RedirectResponse(url="/login", status_code=302)

    user = db.query(Users).filter_by(id=user_info).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    qp_code = request.query_params.get("code")
    if not qp_code:
        raise HTTPException(status_code=400, detail="Code not found")

    code: Code = db.query(Code).filter_by(token=qp_code).first()
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")
    code.is_enable = False
    db.add(code)
    db.commit()

    oidc_auth: OidcAuthorizations = (
        db.query(OidcAuthorizations).filter_by(code_id=code.id).first()
    )
    auth = db.query(Auths).filter_by(id=oidc_auth.auth_id).first()
    consent = oidc_auth.consent

    # アプリケーションの認証情報を取得
    issued_at = datetime.now(timezone.utc)
    access_token_hash = jwt.encode(
        {
            "user_id": user.id,
            "app_id": auth.app_id,
            "scope": consent.scope,
            "issued_at": str(issued_at),
            "exp": str(issued_at + timedelta(minutes=60)),
        },
        "your-secret-key",
        algorithm="HS256",
    )
    access_token = AccessTokens(
        hash=access_token_hash,
        type="access",
        scope=consent.scope,
        issued_at=issued_at,
        exp=issued_at + timedelta(minutes=60),  # 1時間有効
        client_id=auth.app_id,
        user_id=user.id,
    )
    refresh_token_hash = jwt.encode(
        {
            "user_id": user.id,
            "app_id": auth.app_id,
            "scope": consent.scope,
            "issued_at": str(issued_at),
            "exp": str(issued_at + timedelta(days=30)),
        },
        "your-secret-key",
        algorithm="HS256",
    )
    refresh_token = RefreshTokens(
        hash=refresh_token_hash,
        type="refresh",
        scope=consent.scope,
        issued_at=issued_at,
        exp=issued_at + timedelta(days=30),  # 30日有効
        client_id=auth.app_id,
        user_id=user.id,
    )
    db.add_all([access_token, refresh_token])
    db.flush()

    # OIDC トークンを更新
    oidc_token = OidcTokens(
        oidc_authorization_id=oidc_auth.id,
        access_token_id=access_token.id,
        refresh_token_id=refresh_token.id,
    )
    db.add(oidc_token)
    db.commit()

    token_response = {
        "access_token": access_token.hash,
        "token_type": "Bearer",
        "refresh_token": refresh_token.hash,
        # id_tokenをつける
    }
    return JSONResponse(token_response)
