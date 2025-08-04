from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from datetime import timedelta
from typing import Annotated
from db import get_db
import hashlib
import ulid
import os
import jwt
from unique_api.app.model import (
    AccessTokens,
    RefreshTokens,
    IDTokens,
    Users,
    Apps,
    Auths,
    OidcAuthorizations,
    TokenSets,
    Code,
    Sessions,
)
from unique_api.app.schema import AuthenticationRequest
from unique_api.app.crud.auth import get_existing_auth
from unique_api.app.services.authorization import (
    extract_authorized_scopes,
    is_scope_authorized,
    get_or_create_auth,
    create_oidc_authorization,
)
from unique_api.app.services.oauth_utils import validate_redirect_uri


router = APIRouter()
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "../../pages")
)


@router.get("/auth")
async def auth(
    request: Request,
    params: AuthenticationRequest = Depends(),
    db: Session = Depends(get_db),
):
    """
    OIDC 認可フローのためのエンドポイント。
    """
    print("Auth request received:", params.model_dump(exclude_none=True))
    # セッションからユーザ情報を取得
    session_id = request.cookies.get("session_")
    if session_id is None:
        login_action_url = "login"
        login_action_url += f"?{urlencode(params.model_dump(exclude_none=True))}"
        return RedirectResponse(url=login_action_url, status_code=302)

    session = db.query(Sessions).filter_by(id=session_id).first()
    # セッションが保持されていない場合はloginにリダイレクト
    if not session:
        login_action_url = "login"
        login_action_url += f"?{urlencode(params.model_dump(exclude_none=True))}"
        return RedirectResponse(url=login_action_url, status_code=302)

    user = db.query(Users).filter_by(id=session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    app = db.query(Apps).filter_by(client_id=params.client_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Client not found")

    # リダイレクト URI の検証
    redirect_uris = [uri.uri for uri in app.redirect_uris]
    validated_redirect_uri = validate_redirect_uri(params.redirect_uri, redirect_uris)

    # すでに認可されているか確認
    existing_auth = get_existing_auth(db, user.id, app.client_id)
    if existing_auth:
        # すでに認可されている場合は、scopeの権限を確認
        scopes = extract_authorized_scopes(existing_auth)
        if is_scope_authorized(params.scope, scopes):
            print("Existing auth found:", existing_auth.id)
            auth: Auths = get_or_create_auth(db, user.id, app.id)
            oidc_auth: OidcAuthorizations = create_oidc_authorization(
                db, auth, params.scope
            )

            request.session.clear()
            print(f"http://localhost:8000/code?code={oidc_auth.code.token}")
            return RedirectResponse(
                url=f"{params.redirect_uri}?code={oidc_auth.code.token}&state={params.state}",
                status_code=302,
            )

    # 認可されていない場合は認可画面を表示
    # リクエストパラメータをセッションストレージに署名付きで保存する
    request.session["auth_request"] = {
        "client_id": app.client_id,
        "redirect_uri": validated_redirect_uri,
        "scope": params.scope,
        "state": params.state,
        "response_type": params.response_type,
        "auth_at": session.created_at.isoformat(),
        "nonce": params.nonce,
        "code_challenge": params.code_challenge,
        "code_challenge_method": params.code_challenge_method,
    }
    action_url = "auth"
    # 認可画面に必要な情報をテンプレートに渡す
    # ここでは、アプリケーションの情報とユーザ情報を渡す
    auth_data = {
        "app": {
            "name": app.name,
            "client_id": app.client_id,
            "redirect_uris": validated_redirect_uri,
            "scope": params.scope,
        },
        "user": {"name": user.custom_id, "id": user.id},
    }

    response = templates.TemplateResponse(
        "confirm.html",
        {"request": request, "action_url": action_url, "auth_data": auth_data},
    )
    return response


@router.post("/auth")
async def auth_confirm(request: Request, db: Session = Depends(get_db)):
    """
    OIDC 認可フローの確認画面での POST 送信を受けて、認可処理を行う。
    """
    print("Auth confirm request received:", dict(request.query_params))
    # セッションからリクエスト情報を取得
    auth_request = request.session.get("auth_request")
    if auth_request is None:
        raise HTTPException(status_code=400, detail="No auth request found in session")
    # セッションチェック♪
    session_id = request.cookies.get("session_")
    if session_id is None:
        raise HTTPException(status_code=500, detail="Oops, we have a problem.")
    session = db.query(Sessions).filter_by(id=session_id).first()
    # セッションが保持されていない場合はloginにリダイレクト
    if session is None:
        raise HTTPException(status_code=404, detail="Oops, we have a problem.")

    user = db.query(Users).filter_by(id=session.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    app = db.query(Apps).filter_by(client_id=auth_request["client_id"]).first()
    if app is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # すでに認可されているか確認
    auth = get_or_create_auth(db, user.id, app.id)
    # 将来的にamrやacrを使う場合はここでチェックする
    # 現在はpwdオンリー
    oidc_auth = create_oidc_authorization(
        db,
        auth,
        auth_request["scope"],
        nonce=auth_request["nonce"],
        code_challenge=auth_request["code_challenge"],
        code_challenge_method=auth_request["code_challenge_method"],
        acr="pwd",
        amr="pwd",  # JSONでもよい
    )

    request.session.clear()
    print(f"http://localhost:8000/token?code={oidc_auth.code.token}")
    return RedirectResponse(
        url=f"{auth_request['redirect_uri']}?code={oidc_auth.code.token}&state={auth_request['state']}",
        status_code=302,
    )


@router.get("/token")
async def get_code(
    request: Request,
    authorization: Annotated[str | None, Header()],
    db: Session = Depends(get_db),
):
    """
    OIDC 認可コードを取得するエンドポイント。
    """
    print("Get code request received:", dict(request.query_params))

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
    user = db.query(Users).filter_by(id=auth.auth_user_id).first()

    consent = oidc_auth.consent
    app: Apps = db.query(Apps).filter_by(id=auth.app_id).first()
    # Appのシークレットを検証
    if authorization is None or not app.verify_client_secret(authorization):
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    # アプリケーションの認証情報を取得
    access_token_jwt = jwt.encode(
        {
            "iss": "https://auth.uniproject.jp",
            "sub": user.id,
            "aud": app.aud,
            "client_id": auth.app_id,
            "scope": consent.scope,
            "exp": str(code.created_at + timedelta(minutes=60)),
        },
        "your-secret-key",
        algorithm="HS256",
    )
    access_token = AccessTokens(
        hash=hashlib.sha256(access_token_jwt.encode()).hexdigest(),
        type="access",
        scope=consent.scope,
        issued_at=code.created_at,
        exp=code.created_at + timedelta(minutes=60),  # 1時間有効
        client_id=auth.app_id,
        user_id=user.id,
        revoked=False,
    )
    refresh_token_jwt = jwt.encode(
        {
            "iss": "https://auth.uniproject.jp",
            "sub": user.id,
            "client_id": auth.app_id,
            "aud": app.aud,
            "exp": str(code.created_at + timedelta(days=30)),
        },
        "your-secret-key",
        algorithm="HS256",
    )
    refresh_token = RefreshTokens(
        hash=hashlib.sha256(refresh_token_jwt.encode()).hexdigest(),
        type="refresh",
        issued_at=code.created_at,
        exp=code.created_at + timedelta(days=30),  # 30日有効
        client_id=auth.app_id,
        user_id=user.id,
        revoked=False,
    )
    id_token_id = str(ulid.new())
    id_token_jwt = jwt.encode(
        {
            "iss": "https://auth.uniproject.jp",
            "sub": user.id,
            "aud": app.aud,
            "client_id": auth.app_id,
            "scope": consent.scope,
            "exp": str(code.created_at + timedelta(minutes=60)),
            "nonce": code.nonce,
            "auth_time": str(code.created_at),
            "acr": code.acr,
            "amr": code.amr,
            "jti": id_token_id,  # JWT ID
        },
        "your-secret-key",
        algorithm="HS256",
    )
    id_token = IDTokens(
        id=id_token_id,
        hash=hashlib.sha256(id_token_jwt.encode()).hexdigest(),
        type="id",
        issued_at=code.created_at,
        exp=code.created_at + timedelta(minutes=60),  # 1時間有効
        client_id=auth.app_id,
        user_id=user.id,
        aud=app.aud,
        nonce=code.nonce,
        auth_time=code.created_at,
        acr=code.acr,
        amr=code.amr,  # JSONでもよい
    )
    db.add_all([access_token, refresh_token, id_token])
    db.flush()

    # OIDC トークンを更新
    token_set = TokenSets(
        oidc_authorization_id=oidc_auth.id,
        access_token_id=access_token.id,
        refresh_token_id=refresh_token.id,
        id_token_id=id_token.id,
    )
    db.add(token_set)
    db.commit()
    # トークンセットを返す
    # TODO:返却の形をrfc準拠にする
    token_response = {
        "access_token": access_token_jwt,
        "token_type": "Bearer",
        "refresh_token": refresh_token_jwt,
        "id_token": id_token_jwt,
    }
    return JSONResponse(token_response)
