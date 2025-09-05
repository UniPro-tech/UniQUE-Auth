from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from datetime import timedelta, datetime, timezone
from unique_api.app.db import get_db
import hashlib
import ulid
import os
import base64
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
from unique_api.app.services.oauth_utils import validate_redirect_uri, token_authorization
from unique_api.app.schemas.errors import create_token_error_response, OAuthErrorCode
from unique_api.app.services.token import (
    create_access_token,
    create_refresh_token,
    create_id_token,
    generate_at_hash
)
from unique_api.app.config import settings


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

    credentials = f"{app.client_id}:{app.client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    print(
        "Token can be obtained with:\n"
        f"curl -X POST http://localhost:8000/token \\\n"
        "  -H 'Content-Type: application/x-www-form-urlencoded' \\\n"
        f"  -H 'Authorization: Basic {encoded_credentials}'\\\n"
        f"  -d 'grant_type=authorization_code&code={oidc_auth.code.token}&redirect_uri={auth_request['redirect_uri']}'"
    )
    return RedirectResponse(
        url=f"{auth_request['redirect_uri']}?code={oidc_auth.code.token}&state={auth_request['state']}",
        status_code=302,
    )


@router.post("/token")
async def token_endpoint(
    request: Request,
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    code_verifier: str | None = Form(None),
    db: Session = Depends(get_db)
):
    """
    OIDC Token Endpoint - RFC6749 Section 3.2に準拠

    環境変数:
    - REQUIRE_TLS: "true" (デフォルト) の場合、TLSを強制。"false"の場合、TLS検証をスキップ
    - REQUIRE_CLIENT_AUTH: "true" (デフォルト) の場合、クライアント認証を強制。"false"の場合、認証をスキップ
    """
    # TLS要件のチェック
    require_tls = os.getenv("REQUIRE_TLS", "true").lower() == "true"
    if require_tls and not request.url.scheme == "https":
        return create_token_error_response(
            error=OAuthErrorCode.INVALID_REQUEST,
            error_description="HTTPS required"
        )

    # クライアント認証のチェック
    require_client_auth = os.getenv("REQUIRE_CLIENT_AUTH", "true").lower() == "true"
    if require_client_auth:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_CLIENT,
                status_code=401,
                www_authenticate="Basic"
            )

        # クライアント認証の検証
        try:
            client_id, client_secret = token_authorization(auth_header)
            app = db.query(Apps).filter_by(client_id=client_id).first()
            if not app or app.client_secret != client_secret:
                return create_token_error_response(
                    error=OAuthErrorCode.INVALID_CLIENT,
                    status_code=401,
                    www_authenticate="Basic"
                )
        except Exception:
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_CLIENT,
                status_code=401,
                www_authenticate="Basic"
            )

    # grant_typeの検証
    if grant_type != "authorization_code":
        return create_token_error_response(
            error=OAuthErrorCode.UNSUPPORTED_GRANT_TYPE
        )

    # Authorization Codeの検証
    code_obj: Code = db.query(Code).filter_by(token=code).first()
    if not code_obj or not code_obj.is_enable:
        return create_token_error_response(
            error=OAuthErrorCode.INVALID_GRANT
        )

    # Codeの有効期限チェック
    now = datetime.now(timezone.utc)
    code_exp = code_obj.exp.replace(tzinfo=timezone.utc) if code_obj.exp.tzinfo is None else code_obj.exp
    if now > code_exp:
        return create_token_error_response(
            error=OAuthErrorCode.INVALID_GRANT,
            error_description="Authorization code has expired"
        )

    # PKCE検証
    if code_obj.code_challenge is not None:
        if not code_verifier:
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_REQUEST,
                error_description="code_verifier required"
            )

        # code_challengeの検証
        if code_obj.code_challenge_method == "S256":
            verifier_challenge = hashlib.sha256(code_verifier.encode()).digest()
            verifier_challenge = base64.urlsafe_b64encode(verifier_challenge).decode().rstrip("=")
        else:  # plain
            verifier_challenge = code_verifier

        if verifier_challenge != code_obj.code_challenge:
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_GRANT,
                error_description="code_verifier mismatch"
            )

    # OIDCの認可情報を取得
    oidc_auth: OidcAuthorizations = (
        db.query(OidcAuthorizations).filter_by(code_id=code_obj.id).first()
    )
    if not oidc_auth:
        return create_token_error_response(
            error=OAuthErrorCode.INVALID_GRANT,
            error_description="Invalid authorization code"
        )

    auth = db.query(Auths).filter_by(id=oidc_auth.auth_id).first()
    user = db.query(Users).filter_by(id=auth.auth_user_id).first()
    consent = oidc_auth.consent
    app: Apps = db.query(Apps).filter_by(id=auth.app_id).first()

    # redirect_uriの検証
    redirect_uris = [uri.uri for uri in app.redirect_uris]
    if redirect_uri not in redirect_uris:
        return create_token_error_response(
            error=OAuthErrorCode.INVALID_REQUEST,
            error_description="redirect_uri mismatch"
        )

    # Codeを使用済みにする
    code_obj.is_enable = False
    db.add(code_obj)
    db.commit()

    # アクセストークンの生成
    now = datetime.now(timezone.utc)
    access_token_jwt = create_access_token(
        sub=user.id,
        client_id=app.client_id,
        scope=consent.scope,
        aud=app.aud
    )

    # アクセストークンの保存
    access_token = AccessTokens(
        hash=hashlib.sha256(access_token_jwt.encode()).hexdigest(),
        type="access",
        scope=consent.scope,
        issued_at=now,
        exp=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        client_id=app.client_id,
        user_id=user.id,
        revoked=False,
    )

    # リフレッシュトークンの生成
    refresh_token_jwt = create_refresh_token(
        sub=user.id,
        client_id=app.client_id,
        aud=app.aud
    )

    # リフレッシュトークンの保存
    refresh_token = RefreshTokens(
        hash=hashlib.sha256(refresh_token_jwt.encode()).hexdigest(),
        type="refresh",
        issued_at=now,
        exp=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        client_id=app.client_id,
        user_id=user.id,
        revoked=False,
    )

    # at_hashの生成
    at_hash = generate_at_hash(access_token_jwt)

    # IDトークンの生成
    id_token_id = str(ulid.new())
    id_token_jwt = create_id_token(
        sub=user.id,
        aud=app.aud,
        auth_time=int(code_obj.created_at.timestamp()),
        nonce=code_obj.nonce,
        acr=code_obj.acr,
        amr=code_obj.amr,
        at_hash=at_hash,
        azp=app.client_id if isinstance(app.aud, list) and len(app.aud) > 1 else None
    )

    # IDトークンの保存
    id_token = IDTokens(
        id=id_token_id,
        hash=hashlib.sha256(id_token_jwt.encode()).hexdigest(),
        type="id",
        issued_at=now,
        exp=now + timedelta(minutes=settings.ID_TOKEN_EXPIRE_MINUTES),
        client_id=app.client_id,
        user_id=user.id,
        aud=app.aud,
        nonce=code_obj.nonce,
        auth_time=code_obj.created_at,
        acr=code_obj.acr,
        amr=code_obj.amr,
    )

    # トークンの保存
    db.add_all([access_token, refresh_token, id_token])
    db.flush()

    # トークンセットの作成と保存
    token_set = TokenSets(
        oidc_authorization_id=oidc_auth.id,
        access_token_id=access_token.id,
        refresh_token_id=refresh_token.id,
        id_token_id=id_token.id,
    )
    db.add(token_set)
    db.commit()

    # RFC6749に準拠したレスポンスの生成
    token_response = {
        "access_token": access_token_jwt,
        "token_type": "Bearer",
        "expires_in": 3600,  # 1時間
        "refresh_token": refresh_token_jwt,
        "id_token": id_token_jwt,
        "scope": consent.scope
    }

    return JSONResponse(
        content=token_response,
        headers={
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
            "Content-Type": "application/json"
        }
    )
