from fastapi import (
    APIRouter, Depends,
    HTTPException, Request,
    status
)
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware import Middleware
from pydantic import BaseModel
from typing import Optional
from ..cruds.user import get_user_by_name, get_user_by_email, create_user
from .. import schemas
from ..database import get_db

router = APIRouter(
    prefix="/",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


class AuthorizeRequest(BaseModel, Request):
    """ユーザー登録リクエスト"""
    scope: str  # REQUIRED
    response_type: str  # REQUIRED
    client_id: int  # REQUIRED
    redirect_uri: str  # REQUIRED
    state: str  # REQUIRED
    response_mode: Optional[str]  # OPTIONAL
    nonce: str  # OPTIONAL
    display: str  # OPTIONAL
    prompt: str  # OPTIONAL
    max_age: int  # OPTIONAL
    ui_locales: str  # OPTIONAL
    id_token_hint: str  # OPTIONAL
    login_hint: str  # OPTIONAL
    acr_values: str  # OPTIONAL

    def validate_required_fields(self) -> None:
        """AuthorizeRequestの必須フィールドを検証するメソッド"""
        # 必須フィールドのリスト
        # これらのフィールドはNoneであってはいけない
        required_fields = ["scope", "response_type", "client_id", "redirect_uri", "state"]
        for field in required_fields:
            if getattr(self, field) is None:
                raise ValueError(f"The field '{field}' is required and cannot be None.")
        
        # display変数の値を検証
        # displayはpage, popup, touch, wapのいずれかである必要がある
        display_values = ["page", "popup", "touch", "wap"]
        if self.display not in display_values:
            raise ValueError(f"The field 'display' must be one of {display_values}.")
        
        # prompt変数の値を検証
        # promptはnone, login, consent, select_accountのいずれかである必要がある
        prompt_values = ["none", "login", "consent", "select_account"]
        if self.prompt not in prompt_values:
            raise ValueError(f"The field 'prompt' must be one of {prompt_values}.")


@router.post("/authorize", response_model=schemas.User)
async def authorize(
            request: AuthorizeRequest,
            session: Session = Depends(get_db)
        ):
    """
    OIDC認証・認可リクエストエンドポイント
    """
    # リクエストパラメータの検証
    try:
        request.validate_required_fields()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # 未ログインの場合は/loginに302リダイレクト
    if not request.session.get("authenticated"):
        # セッションストレージにリクエストパラメータを保存
        request.session["client_id"] = request.client_id
        request.session["redirect_uri"] = request.redirect_uri
        request.session["scope"] = request.scope
        request.session["state"] = request.state
        request.session["response_type"] = request.response_type
        request.session["nonce"] = request.nonce
        request.session["display"] = request.display
        request.session["prompt"] = request.prompt
        request.session["max_age"] = request.max_age
        request.session["ui_locales"] = request.ui_locales
        request.session["id_token_hint"] = request.id_token_hint
        request.session["login_hint"] = request.login_hint
        request.session["acr_values"] = request.acr_values
        # 追加のリクエストパラメータもセッションに保存する場合はここに追加

        # ログイン画面にリダイレクト
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # セッションクッキーを使用し判断する

    # ログインUIを表示する


    # ユーザーがすでに認可されているか確認

    # ユーザーが認可されていない場合は、認可画面を表示する

    # ユーザーの認可& トークンの発行


@router.get("/login")
async def login_get(request: Request):
    """
    OIDC 認可フロー開始時、外部クライアントから
    リクエストパラメータを検証して request.session に保存した上で
    このエンドポイントにリダイレクトさせる想定です。
    GET では単にログインフォームを表示。
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
):
    # 1) 認証
    user = authenticate(username, password)
    if not user:
        # 認証失敗時は画面にエラーメッセージを渡す
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "ユーザー名またはパスワードが正しくありません。"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # 2) 認証成功 → セッションに情報を保存
    session = request.session

    # --- すでにある OIDC リクエストパラメータ (例) ---
    # session["client_id"]
    # session["redirect_uri"]
    # session["scope"]
    # session["state"]
    # session["response_type"]
    # session["code_challenge"], session["code_challenge_method"]
    # session["prompt"], session["nonce"], session["login_hint"]

    # --- ここから追加で保存する認証情報 ---
    session["user_id"]       = user["id"]
    session["auth_time"]     = int(time.time())         # UNIXタイムスタンプ
    session["remember_me"]   = remember_me              # boolean
    session["authenticated"] = True

    # 3) /authorize にリダイレクト
    return RedirectResponse(url="/authorize", status_code=status.HTTP_302_FOUND)