from urllib.parse import urlparse, parse_qs
from .test_utils import (
    create_test_client_credentials,
    decode_id_token,
    validate_id_token,
    generate_pkce_params
)


def test_authorization_code_flow_basic(client, test_user, test_app):
    """基本的なAuthorization Code Flowのテスト"""
    # 1. 認可リクエスト
    auth_params = {
        "response_type": "code",
        "client_id": test_app.id,
        "redirect_uri": "http://localhost:3000/callback",
        "scope": "openid",
        "state": "test_state",
        "nonce": "test_nonce"
    }
    response = client.get("/auth", params=auth_params)
    assert response.status_code == 302
    assert response.headers["location"].startswith("/login")

    # 2. ログイン
    login_data = {
        "custom_id": test_user.custom_id,
        "password": "test_password"
    }
    response = client.post("/login", data=login_data, params=auth_params)
    assert response.status_code == 302
    assert response.headers["location"].startswith("/auth")

    # 3. 認可の同意
    response = client.post("/auth")
    assert response.status_code == 302
    callback_url = response.headers["location"]
    assert callback_url.startswith("http://localhost:3000/callback")

    # 認可コードの取得
    query_params = parse_qs(urlparse(callback_url).query)
    assert "code" in query_params
    assert query_params["state"][0] == "test_state"
    code = query_params["code"][0]

    # 4. トークンリクエスト
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:3000/callback"
    }
    headers = {
        "Authorization": create_test_client_credentials(
            test_app.id,
            "test_client_secret"
        )
    }
    response = client.post("/token", data=token_data, headers=headers)
    assert response.status_code == 200
    token_response = response.json()

    # レスポンスの検証
    assert "access_token" in token_response
    assert "token_type" in token_response
    assert token_response["token_type"] == "Bearer"
    assert "expires_in" in token_response
    assert "refresh_token" in token_response
    assert "id_token" in token_response

    # IDトークンの検証
    id_token = decode_id_token(token_response["id_token"])
    validate_id_token(
        id_token,
        expected_sub=test_user.id,
        expected_aud=test_app.id,
        expected_nonce="test_nonce"
    )


def test_authorization_code_flow_with_pkce(client, test_user, test_app):
    """PKCEを使用したAuthorization Code Flowのテスト"""
    # PKCE パラメータの生成
    code_verifier, code_challenge = generate_pkce_params()

    # 1. 認可リクエスト（PKCE付き）
    auth_params = {
        "response_type": "code",
        "client_id": test_app.id,
        "redirect_uri": "http://localhost:3000/callback",
        "scope": "openid",
        "state": "test_state",
        "nonce": "test_nonce",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    response = client.get("/auth", params=auth_params)
    assert response.status_code == 302
    assert response.headers["location"].startswith("/login")

    # 2. ログイン
    login_data = {
        "custom_id": test_user.custom_id,
        "password": "test_password"
    }
    response = client.post("/login", data=login_data, params=auth_params)
    assert response.status_code == 302
    assert response.headers["location"].startswith("/auth")

    # 3. 認可の同意
    response = client.post("/auth")
    assert response.status_code == 302
    callback_url = response.headers["location"]
    query_params = parse_qs(urlparse(callback_url).query)
    code = query_params["code"][0]

    # 4. トークンリクエスト（code_verifier付き）
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:3000/callback",
        "code_verifier": code_verifier
    }
    headers = {
        "Authorization": create_test_client_credentials(
            test_app.id,
            "test_client_secret"
        )
    }
    response = client.post("/token", data=token_data, headers=headers)
    assert response.status_code == 200
    token_response = response.json()

    # IDトークンの検証
    id_token = decode_id_token(token_response["id_token"])
    validate_id_token(
        id_token,
        expected_sub=test_user.id,
        expected_aud=test_app.id,
        expected_nonce="test_nonce"
    )


def test_authorization_code_flow_error_cases(client, test_user, test_app):
    """エラーケースのテスト"""
    # 1. 無効なクライアントID
    auth_params = {
        "response_type": "code",
        "client_id": "invalid_client_id",
        "redirect_uri": "http://localhost:3000/callback",
        "scope": "openid",
        "state": "test_state"
    }
    response = client.get("/auth", params=auth_params)
    assert response.status_code == 404

    # 2. 無効なリダイレクトURI
    auth_params["client_id"] = test_app.id
    auth_params["redirect_uri"] = "http://invalid.example.com"
    response = client.get("/auth", params=auth_params)
    assert response.status_code == 400

    # 3. 無効な認可コード
    token_data = {
        "grant_type": "authorization_code",
        "code": "invalid_code",
        "redirect_uri": "http://localhost:3000/callback"
    }
    headers = {
        "Authorization": create_test_client_credentials(
            test_app.id,
            "test_client_secret"
        )
    }
    response = client.post("/token", data=token_data, headers=headers)
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_grant"

    # 4. 無効なクライアント認証
    auth_params = {
        "response_type": "code",
        "client_id": test_app.id,
        "redirect_uri": "http://localhost:3000/callback",
        "scope": "openid",
        "state": "test_state"
    }
    response = client.get("/auth", params=auth_params)
    assert response.status_code == 302

    response = client.post("/login", data={
        "custom_id": test_user.custom_id,
        "password": "test_password"
    }, params=auth_params)
    assert response.status_code == 302

    response = client.post("/auth")
    assert response.status_code == 302
    callback_url = response.headers["location"]
    query_params = parse_qs(urlparse(callback_url).query)
    code = query_params["code"][0]

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:3000/callback"
    }
    headers = {
        "Authorization": create_test_client_credentials(
            test_app.id,
            "invalid_secret"
        )
    }
    response = client.post("/token", data=token_data, headers=headers)
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_client"
