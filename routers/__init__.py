from fastapi import (
    APIRouter, Depends,
    HTTPException, Request,
    Query, Form
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware import Middleware
from pydantic import BaseModel, Field
from typing import Optional
from urllib.parse import urlencode
import json
from cruds.user import (
    get_user_by_email,
    get_user_by_id,
    create_user,
)
from cruds.client import (
    get_client_by_id,
    get_client_by_id,
)
from models.session import Client
from database import get_db

templates = Jinja2Templates(directory="../pages")

router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/authorize")
async def authorize(
        request: Request,
        db: Session = Depends(get_db)
):
    """
    OIDC認証・認可リクエストエンドポイント
    """
    # クエリパラメータを取得
    query_params = dict(request.query_params)

    # 未ログインの場合は/loginに302リダイレクト
    if not request.cookies.get("session"):
        url_params = urlencode(query_params)
        response = RedirectResponse(url=f"/login?{url_params}", status_code=302)
        return response

    # リダイレクトURIの検証
    # リダイレクトURIはクライアントのリダイレクトURIのいずれかである必要がある
    redirect_uri = query_params["redirect_uri"]
    client: Client = get_client_by_id(db, query_params["client_id"])
    if redirect_uri not in client.redirect_uris:
        # リダイレクトURLが無効
        return RedirectResponse(
            url="/error?error=Invalid redirect_uri",
            error_description="Invalid redirect_uri",
            status_code=302
        )

    # 必須フィールドのリスト
    # これらのフィールドはNoneであってはいけない
    required_fields = ["scope", "response_type", "client_id", "redirect_uri", "state"]
    missing_fields = [field for field in required_fields if field not in query_params]
    if missing_fields:
        # 必須フィールドが不足している場合は、エラーレスポンスを返す
        error_response = {
            "error": "invalid_request",
            "error_description": f"Missing required fields: {', '.join(missing_fields)}",
            "state": query_params.get("state"),
        }
        return RedirectResponse(
            url=f"{query_params.get('redirect_uri')}?{urlencode(error_response)}",
            status_code=302
        )

    # prompt変数の値を検証
    # promptはnone, login, consent, select_accountのいずれかである必要がある
    prompt_values = ["none", "login", "consent", "select_account"]
    if query_params.get("prompt") not in prompt_values:
        raise ValueError(f"The field 'prompt' must be one of {prompt_values}.")
    if query_params.get("prompt") == "none" and query_params.get("display"):
        # promptがnoneかつdisplayが指定されている場合はエラー
        error_response = {
            "error": "consent_required",
            "error_description": "prompt=none and display cannot be used together",
            "state": query_params.get("state"),
        }
        return RedirectResponse(
            url=f"{query_params.get('redirect_uri')}?{urlencode(error_response)}",
            status_code=302
        )

    # display変数の値を検証
    # displayはpage, popup, touch, wapのいずれかである必要がある
    # displayがNoneの場合は、pageにする
    if query_params.get("display") is None:
        query_params["display"] = "page"
    display_values = ["page", "popup", "touch", "wap"]
    if query_params.get("display") not in display_values:
        print(f"e: {query_params.get('display')}")
        error_response = {
            "error": "invalid_request",
            "error_description": f"Invalid display value: {query_params.get('display')}",
            "state": query_params.get("state"),
        }
        return RedirectResponse(
            url=f"{query_params.get('redirect_uri')}?{urlencode(error_response)}",
            status_code=302
        )

    # ユーザーがすでに認可されているか確認
    print("user_id", json.loads(request.cookies.get("session"))["id"])
    user = get_user_by_id(db, json.loads(request.cookies.get("session"))["id"])
    auth_client_ids = [client.client_id for client in user.sessions]
    if query_params["client_id"] in auth_client_ids:
        # ユーザーが認可済みのクライアントにリダイレクト
        # TODO: ここで認可コードを発行する
        return RedirectResponse(
            url=f"{query_params.get('redirect_uri')}?{urlencode({'code': user.get_auth_code()})}",
            status_code=302
        )

    app = get_app_by_id(db, client_id)
    # ユーザーが認可されていない場合は、認可画面を表示する
    # クッキーに認可に必要なリクエストパラメータを保存
    # クッキーに保存するため、辞書に変換してエンコード
    try:
        raw_params = auth_request.model_dump()
        # None の値を除外
        filtered_params = {k: v for k, v in raw_params.items() if v is not None}
        query_string = urlencode(filtered_params)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid auth request cookie")
    # 認可画面にリダイレクト（302）
    redirect_url = f"/authorize?{query_string}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(key="auth_request", value=json.dumps(auth_request.model_dump()), httponly=True, max_age=300)

    # ユーザーの認可& トークンの発行


@router.post("/authorize")
async def authorize_post(
    request: Request,
    action: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    ユーザーの認可を受けて、トークンを発行するエンドポイント
    このあとの認証に用いる情報はクッキーより取得する
    """
    # クッキーから認可リクエストを取得
    auth_cookie = request.cookies.get("auth_request")
    if not auth_cookie:
        raise HTTPException(status_code=400, detail="Missing auth request")

    # ユーザーの認可を確認
    if action != "allow":
        # ユーザーが認可しなかった場合は、エラーレスポンスを返す
        error_response = {
            "error": "access_denied",
            "error_description": "User denied the request",
            "state": filtered_params.get("state"),
        }
        return RedirectResponse(url=f"/error?{urlencode(error_response)}", status_code=302)
    
    # クエリ文字列として使うため、辞書に変換してエンコード
    try:
        raw_params: dict = json.loads(auth_cookie)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid auth request cookie")
    
    #  認証認可成功
    # ユーザークライアントの作成’
    user = get_user_by_id(db, json.loads(request.cookies.get("session"))["id"])
    app = get_app_by_id(db, raw_params["client_id"])
    user_client = Client(
        user=user,
        app=app,
    )
    query_string = urlencode(filtered_params)
    # 認可された場合は、/tokenにリダイレクト（302）
    redirect_url = f"/token?{query_string}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.delete_cookie("auth_request")
    return response


# ログインフォームの流れ
@router.get("/login")
async def login_get(request: Request):
    """
    OIDC 認可フロー開始時、外部クライアントから
    リクエストパラメータを検証して request.session に保存した上で
    このエンドポイントにリダイレクトさせる想定です。
    GET では単にログインフォームを表示。
    """
    query_params = dict(request.query_params)
    query_string = urlencode(query_params)
    action_url = "/login"
    if query_string:
        action_url += f"?{query_string}"
    return templates.TemplateResponse("login.html", {"request": request, "action_url": action_url})


# リダイレクトされた際に存在したクエリパラメータをそのままauthorizeに渡す
# ログインセッションを作成する
@router.post("/login")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # ユーザー名とパスワードを検証
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user.verify_password(password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # 認証に成功した場合、セッションにユーザー情報を保存

    # クエリパラメータをauthorizeに渡す
    query_params = dict(request.query_params)
    query_string = urlencode(query_params)

    # クエリパラメータが存在する場合は、/authorizeにリダイレクト
    if query_string:
        redirect_url = f"/authorize?{query_string}"
    else:
        redirect_url = "/home"

    response = RedirectResponse(url=redirect_url, status_code=302)
    # TODO: 本番環境ではhttponly=Trueにする
    response.set_cookie(
        key="session",
        value=json.dumps({"id": user.id}),
        httponly=False,
        max_age=300
    )

    return response
