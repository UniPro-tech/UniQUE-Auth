from fastapi import APIRouter, Request, Depends, Form
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
from unique_api.app.services.authorization import (
    get_or_create_auth,
    create_oidc_authorization,
)
from unique_api.app.services.oauth_utils import (
    validate_redirect_uri,
    token_authorization,
)
from unique_api.app.schemas.errors import create_token_error_response, OAuthErrorCode
from unique_api.app.services.token import generate_at_hash, token_maker, TokenPayload

from unique_api.app.config import settings
from unique_api.app.services.token.hash import make_token_hasher


router = APIRouter()


@router.post("/auth")
async def auth_confirm(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(...),
    state: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    OIDC 認可フローの確認画面での POST 送信を受けて、認可処理を行う。
    フォーム送信 (hidden inputs: client_id, redirect_uri, scope, state) を想定している。
    セッションに保存された nonce / PKCE 情報があれば補完して使用する。
    """
    print(
        "Auth confirm (form) request received:",
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
        },
    )

    # セッションから補完情報（nonce, PKCE 等）を取得
    session_auth_request = request.session.get("auth_request", {})

    # セッションチェック（cookie 名が環境によって異なる場合があるため両方確認）
    session_id = request.cookies.get("unique-sid") or request.cookies.get("session_")
    if session_id is None:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error?{urlencode({'error': 'session_missing', 'error_description': 'Session is missing'})}",
            status_code=302,
        )

    session = db.query(Sessions).filter_by(id=session_id).first()
    if session is None:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error?{urlencode({'error': 'session_invalid', 'error_description': 'Session is invalid'})}",
            status_code=302,
        )

    user = db.query(Users).filter_by(id=session.user_id).first()
    if user is None:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error?{urlencode({'error': 'user_not_found', 'error_description': 'User not found'})}",
            status_code=302,
        )

    # client_id はフォームで受け取る
    app = db.query(Apps).filter_by(id=client_id).first()
    if app is None:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error?{urlencode({'error': 'client_not_found', 'error_description': 'Client not found'})}",
            status_code=302,
        )

    # redirect_uri の検証
    redirect_uris = [uri.uri for uri in app.redirect_uris]
    validated_redirect_uri = validate_redirect_uri(redirect_uri, redirect_uris)

    if isinstance(validated_redirect_uri, RedirectResponse):
        return validated_redirect_uri

    # 認可（Auth）を取得/作成
    auth = get_or_create_auth(db, user.id, app.id)

    # セッションから補完できるなら nonce / PKCE を使う
    nonce = session_auth_request.get("nonce")
    code_challenge = session_auth_request.get("code_challenge")
    code_challenge_method = session_auth_request.get("code_challenge_method")

    oidc_auth = create_oidc_authorization(
        db,
        auth,
        scope,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        acr="pwd",
        amr="pwd",
    )

    request.session.clear()

    credentials = f"{app.id}:{app.client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    print(
        "Token can be obtained with:\n"
        f"curl -X POST http://localhost:8000/token \\\n+  -H 'Content-Type: application/x-www-form-urlencoded' \\\n+  -H 'Authorization: Basic {encoded_credentials}'\\\n"
        f"  -d 'grant_type=authorization_code&code={oidc_auth.code.token}&redirect_uri={validated_redirect_uri}'"
    )

    resp_state = state or session_auth_request.get("state")
    return RedirectResponse(
        url=f"{validated_redirect_uri}?code={oidc_auth.code.token}&state={resp_state}",
        status_code=302,
    )


@router.post("/token")
async def token_endpoint(
    request: Request,
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    code_verifier: str | None = Form(None),
    db: Session = Depends(get_db),
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
            error=OAuthErrorCode.INVALID_REQUEST, error_description="HTTPS required"
        )

    # クライアント認証のチェック
    require_client_auth = os.getenv("REQUIRE_CLIENT_AUTH", "true").lower() == "true"
    if require_client_auth:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_CLIENT,
                status_code=401,
                www_authenticate="Basic",
            )

        # クライアント認証の検証
        try:
            client_id, client_secret = token_authorization(auth_header)
            app = db.query(Apps).filter_by(id=client_id).first()
            if not app or app.client_secret != client_secret:
                return create_token_error_response(
                    error=OAuthErrorCode.INVALID_CLIENT,
                    status_code=401,
                    www_authenticate="Basic",
                )
        except Exception:
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_CLIENT,
                status_code=401,
                www_authenticate="Basic",
            )

    # grant_typeの検証
    if grant_type != "authorization_code":
        return create_token_error_response(error=OAuthErrorCode.UNSUPPORTED_GRANT_TYPE)

    # Authorization Codeの検証
    code_obj: Code = db.query(Code).filter_by(token=code).first()
    if not code_obj or not code_obj.is_enable:
        return create_token_error_response(error=OAuthErrorCode.INVALID_GRANT)

    # Codeの有効期限チェック
    now = datetime.now(timezone.utc)
    code_exp = (
        code_obj.exp.replace(tzinfo=timezone.utc)
        if code_obj.exp.tzinfo is None
        else code_obj.exp
    )
    if now > code_exp:
        return create_token_error_response(
            error=OAuthErrorCode.INVALID_GRANT,
            error_description="Authorization code has expired",
        )

    # PKCE検証
    if code_obj.code_challenge is not None:
        if not code_verifier:
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_REQUEST,
                error_description="code_verifier required",
            )

        # code_challengeの検証
        if code_obj.code_challenge_method == "S256":
            verifier_challenge = hashlib.sha256(code_verifier.encode()).digest()
            verifier_challenge = (
                base64.urlsafe_b64encode(verifier_challenge).decode().rstrip("=")
            )
        else:  # plain
            verifier_challenge = code_verifier

        if verifier_challenge != code_obj.code_challenge:
            return create_token_error_response(
                error=OAuthErrorCode.INVALID_GRANT,
                error_description="code_verifier mismatch",
            )

    # OIDCの認可情報を取得
    oidc_auth: OidcAuthorizations = (
        db.query(OidcAuthorizations).filter_by(code_id=code_obj.id).first()
    )
    if not oidc_auth:
        return create_token_error_response(
            error=OAuthErrorCode.INVALID_GRANT,
            error_description="Invalid authorization code",
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
            error_description="redirect_uri mismatch",
        )

    # Codeを使用済みにする
    code_obj.is_enable = False
    db.add(code_obj)
    db.commit()

    hash_maker = make_token_hasher(
        algorithm=settings.JWT_ALGORITHM,
        private_key_path=settings.RSA_PRIVATE_KEY_PATH,
        public_key_path=settings.RSA_PUBLIC_KEY_PATH,
    )

    # アクセストークンの生成
    now = datetime.now(timezone.utc)
    access_token_data = TokenPayload(
        iss="unique-api",
        sub=user.id,
        aud=app.id,
        exp=int(
            (now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        ),
        iat=int(now.timestamp()),
        jti=str(ulid.new()),
        scope=consent.scope,
    )
    access_token_oj = token_maker(hash_maker, "access_token", access_token_data)
    access_token_jwt = access_token_oj.generate_token()

    # アクセストークンの保存
    access_token = AccessTokens(
        hash=hashlib.sha256(access_token_jwt.encode()).hexdigest(),
        type="access",
        scope=consent.scope,
        issued_at=now,
        exp=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        client_id=app.id,
        user_id=user.id,
        revoked=False,
    )

    # リフレッシュトークンの生成
    refresh_token_data = TokenPayload(
        iss="unique-api",
        sub=user.id,
        aud=app.id,
        exp=int((now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        iat=int(now.timestamp()),
        jti=str(ulid.new()),
        scope=consent.scope,
    )
    refresh_token_oj = token_maker(hash_maker, "refresh_token", refresh_token_data)
    refresh_token_jwt = refresh_token_oj.generate_token()

    # リフレッシュトークンの保存
    refresh_token = RefreshTokens(
        hash=hashlib.sha256(refresh_token_jwt.encode()).hexdigest(),
        type="refresh",
        issued_at=now,
        exp=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        client_id=app.id,
        user_id=user.id,
        revoked=False,
    )

    # at_hashの生成
    at_hash = generate_at_hash(access_token_jwt, algorithm="HS256")

    # IDトークンの生成
    id_token_id = str(ulid.new())
    id_token_data = TokenPayload(
        sub=user.id,
        aud=app.id,
        auth_time=int(code_obj.created_at.timestamp()),
        nonce=code_obj.nonce,
        acr=code_obj.acr,
        amr=code_obj.amr,
        at_hash=at_hash,
        azp=app.id if isinstance(app.id, list) and len(app.id) > 1 else None,
    )
    id_token_oj = token_maker(
        hash_maker,
        "id_token",
        id_token_data,
        clalms={
            "email": user.email,
            "email_verified": True,
        },
    )
    id_token_jwt = id_token_oj.generate_token()

    # IDトークンの保存
    id_token = IDTokens(
        id=id_token_id,
        hash=hashlib.sha256(id_token_jwt.encode()).hexdigest(),
        type="id",
        issued_at=now,
        exp=now + timedelta(minutes=settings.ID_TOKEN_EXPIRE_MINUTES),
        client_id=app.id,
        user_id=user.id,
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
        "expires_in": int(
            (now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
        ),  # 1時間
        "refresh_token": refresh_token_jwt,
        "id_token": id_token_jwt,
        "scope": consent.scope,
    }

    return JSONResponse(
        content=token_response,
        headers={
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
            "Content-Type": "application/json",
        },
    )
