# crudのテストファイル
from database import Base, engine, get_db

from models import (
    Client, User,
    Session, AccessToken,
    RefreshToken, IDToken
)
from cruds.client import (
    create_client,
    get_client_by_id,
    update_client,
    delete_client_by_id,
    create_redirect_uri,
    delete_redirect_uri
)
from cruds.user import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user_by_id
)
from cruds.session import (
    create_session,
    get_session_by_id,
    delete_session_by_id
)
from cruds.token import (
    create_access_token,
    get_access_token_by_id,
    update_access_token,
    delete_access_token_by_id,
    create_refresh_token,
    get_refresh_token_by_id,
    update_refresh_token,
    delete_refresh_token_by_id,
    create_id_token,
    get_id_token_by_id,
    update_id_token,
    delete_id_token_by_id
)

session = next(get_db())


# テスト用のDBを作成
def setup_module(module):
    Base.metadata.create_all(bind=engine)
    # テスト用のDBを作成
    # ここで必要なテストデータを挿入することもできます
    # 例: create_client(session, ...)
    user_list = [
        {
            "username": "testuser1",
            "password": "password1",
            "email": "test@test.com"
        },
        {
            "username": "testuser2",
            "password": "password2",
            "email": "test2@test.com"
        }
    ]
    for user in user_list:
        create_user(session, **user)
    client_list = [
        {
            "client_id": "test_client_1",
            "name": "Test Client 1",
            "client_type": "confidential",
            "client_secret": "client_secret_1",
            "redirect_uris": ["http://localhost:8000/callback"]
        },
        {
            "client_id": "test_client_2",
            "name": "Test Client 2",
            "client_type": "public",
            "client_secret": "client_secret_2",
            "redirect_uris": ["http://localhost:8000/callback"]
        }
    ]
    for client in client_list:
        create_client(session, **client)
