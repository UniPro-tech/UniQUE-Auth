from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from datetime import datetime, timedelta
from db import get_db
import hashlib
import jwt
from uuid import uuid4
import base64
from model import User, Session as UserSession, App, Auth, Consent, OIDCTokens, Token


router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/login")
async def login(
    request: Request
):
    """
    OIDC 認可フロー開始時、外部クライアントから
    リクエストパラメータを検証して request.session に保存した上で
    このエンドポイントにリダイレクトさせる想定です。
    GET では単にログインフォームを表示。
    """
    action_url = "/login"
    if request.query_params:
        action_url += f"?{urlencode(request.query_params)}"
    return templates.TemplateResponse("login.html", {"request": request, "action_url": action_url})


@router.post("/login")
async def login_post(
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    ログインフォームの POST 送信を受けて、認証処理を行う。
    認証成功時はセッションにユーザ情報を保存し、リダイレクトする。
    """
    print("Login POST request received:", request.query_params._dict)
    # ここでユーザ認証を行う
    # 例えば、email と password を使ってユーザを検索し、認証が成功したら
    # セッションにユーザ情報を保存する
    validated_user = db.query(User).filter_by(name=name, passwd_hash=hashlib.sha256(password.encode()).hexdigest()).first()

    if validated_user is None:
        # 認証失敗
        response = HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
        return response

    # 認証成功
    request.session["user"] = f"{{'id': {validated_user.id}, 'name': {validated_user.name}}}"

    if request.query_params._dict == {}:
        redirect_url = "/"
    # OIDC 認可フローの場合、リダイレクト先の URL に
    elif request.query_params._dict.get("redirect_uri"):  # TODO:リダイレクト先の URI が指定されている場合
        # リダイレクト先の URL にクエリパラメータを追加
        redirect_url = "/auth?" + urlencode(request.query_params._dict)

    # セッションを作成
    session = UserSession(
        user_id=validated_user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent", ""),
        created_at=datetime.now()
    )
    db.add(session)
    db.commit()
    # リダイレクト
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(key="user_id", value=validated_user.id)
    return response


@router.get("/logout")
async def logout(
    request: Request
):
    """
    ログアウト処理を行うエンドポイント。
    """
    request.session.clear()
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="user_id")
    return response


@router.get("/signup")
async def signup(
    request: Request
):
    """
    サインアップ処理を行うエンドポイント。
    """
    action_url = "/signup"
    if request.query_params:
        action_url += f"?{urlencode(request.query_params)}"
    return templates.TemplateResponse("signup.html", {"request": request, "action_url": action_url})


@router.post("/signup")
async def signup_post(
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    サインアップフォームの POST 送信を受けて、ユーザ登録処理を行う。
    登録成功時はログインページにリダイレクトする。
    """
    print("Signup POST request received:", request.query_params._dict)

    # ユーザ名の重複チェック
    existing_user = db.query(User).filter_by(name=name).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "User already exists"})

    # 新規ユーザの作成
    new_user = User(
        name=name,
        passwd_hash=hashlib.sha256(password.encode()).hexdigest(),
        created_at=datetime.now()
    )
    db.add(new_user)
    db.commit()

    # 登録成功後はログインページにリダイレクト
    return RedirectResponse(url="/login", status_code=302)


@router.get("/auth")
async def auth(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    OIDC 認可フローのためのエンドポイント。
    """
    print("Auth request received:", request.query_params._dict)
    request_query_params = request.query_params._dict
    # セッションからユーザ情報を取得
    user_info = request.cookies.get("user_id")
    if not user_info:
        raise RedirectResponse(url="/login", status_code=302)

    user = db.query(User).filter_by(id=int(user_info)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    client_id = request.query_params.get("client_id")

    app = db.query(App).filter_by(client_id=client_id).first()
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
    existing_auth = db.query(Auth).filter_by(auth_user_id=user.id, app_id=app.id).first()
    if existing_auth:
        if set(request_query_params["scope"].split(" ")) <= set(existing_auth.consent.scope.split(" ")):
            redirect_uris = [uri.uri for uri in app.redirect_uris]
            print("Existing auth found:", existing_auth.id, "Redirect URIs:", redirect_uris)
            # TODO: codeを生成してリダイレクト
            if request_query_params["redirect_uri"] not in redirect_uris:
                raise HTTPException(status_code=400, detail="Redirect URI not allowed")
        return RedirectResponse(url=request_query_params["redirect_uri"], status_code=302)

    # 認可されていない場合は認可画面を表示
    action_url = f"/auth/confirm?{urlencode(request.query_params)}"

    auth_data = {
        "app": {
            "name": app.name,
            "client_id": app.client_id,
            "redirect_uris": [uri.uri for uri in app.redirect_uris],
            "scope": request_query_params.get("scope", "default")
        },
        "user": {
            "name": user.name,
            "id": user.id
        },
    }

    response = templates.TemplateResponse("confirm.html", {"request": request, "action_url": action_url, "auth_data": auth_data})
    return response


@router.post("/auth/confirm")
async def auth_confirm(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    OIDC 認可フローの確認画面での POST 送信を受けて、認可処理を行う。
    """
    print("Auth confirm request received:", request.query_params._dict)
    user_info = request.cookies.get("user_id")
    if not user_info:
        raise RedirectResponse(url="/login", status_code=302)

    user = db.query(User).filter_by(id=int(user_info)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    client_id = request.query_params.get("client_id")
    app = db.query(App).filter_by(client_id=client_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Client not found")

    # すでに認可されているか確認
    existing_auth = db.query(Auth).filter_by(auth_user_id=user.id, app_id=app.id).first()
    if existing_auth is None:
        # 新規認可を作成
        existing_auth = Auth(
            auth_user_id=user.id,
            app_id=app.id,
            created_at=datetime.now()
        )
        db.add(existing_auth)
        db.flush()


    # リダイレクト先の URI を取得
    redirect_uri = request.query_params.get("redirect_uri")

    return RedirectResponse(
        url=f"/code?code={oidc_tokens.code}&redirect_uri={redirect_uri}",
        status_code=302
    )


@router.get("/code")
async def get_code(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    OIDC 認可コードを取得するエンドポイント。
    """
    print("Get code request received:", request.query_params._dict)
    user_info = request.cookies.get("user_id")
    if not user_info:
        raise RedirectResponse(url="/login", status_code=302)

    user = db.query(User).filter_by(id=int(user_info)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")

    oidc_tokens = db.query(OIDCTokens).filter_by(code=code).first()
    if not oidc_tokens:
        raise HTTPException(status_code=404, detail="OIDC Tokens not found")

    auth = db.query(Auth).filter_by(id=oidc_tokens.auths_id).first()
    consent = db.query(Consent).filter_by(auth_id=auth.id).first()

    # アプリケーションの認証情報を取得
    access_token_hash = jwt.encode(
        {"user_id": user.id, "app_id": auth.app_id, "scope": consent.scope},
        "your-secret-key",
        algorithm="HS256"
    )
    access_token = Token(
        hash=access_token_hash,
        type="access",
        scope=consent.scope,
        issued_at=datetime.now(),
        exp=datetime.now() + timedelta(minutes=60),  # 1時間有効
        client_id=auth.app_id,
        user_id=user.id
    )
    refresh_token_hash = jwt.encode(
        {"user_id": user.id, "app_id": auth.app_id, "scope": consent.scope},
        "your-secret-key",
        algorithm="HS256"
    )
    refresh_token = Token(
        hash=refresh_token_hash,
        type="refresh",
        scope=consent.scope,
        issued_at=datetime.now(),
        exp=datetime.now() + timedelta(days=30),  # 30日有効
        client_id=auth.app_id,
        user_id=user.id
    )
    db.add_all([access_token, refresh_token])
    db.flush()

    # OIDC トークンを更新
    oidc_tokens.access_token_id = access_token.id
    oidc_tokens.refresh_token_id = refresh_token.id
    db.commit()

    # リダイレクト先の URI を取得
    redirect_uri = request.query_params.get("redirect_uri")
    if not redirect_uri:
        raise HTTPException(status_code=400, detail="Redirect URI not provided")
    # リダイレクト URI に認可コードを付与してリダイレクト
    return 
