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
    get_access_token_by_hash,
    update_access_token_status,
    delete_access_token_by_hash,
    create_refresh_token,
    get_refresh_token_by_hash,
    update_refresh_token_status,
    delete_refresh_token_by_hash,
    create_id_token,
    get_id_token_by_sub,
    delete_id_token_by_hash
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


# userのCRUDテスト
# 1. 作成

# 2. 検索

# 3. 更新

# 4. 削除

# 5. useridが存在しない場合の処理

# 6. ユーザー名の重複チェック

# 7. メールアドレスの重複チェック

# 8. パスワードのハッシュ化と検証

# 9. ユーザーデータの更新時間が正しく更新されること

# 10. ユーザーの削除が正しく行われること


# clientのCRUDテスト
# 1. 作成

# 2. 検索

# 3. 更新

# 4. 削除

# 5. client_idが存在しない場合の処理

# 6. client_idの重複チェック

# 7. リダイレクトURIの作成

# 8. リダイレクトURIの削除

# 9. リダイレクトURIの重複チェック

# 10. クライアントデータの更新時間が正しく更新されること

# 11. クライアントの削除が正しく行われること

# 12. クライアントが削除された場合、関連するリダイレクトURIも削除されること

# sessionのCRUDテスト
# 1. 作成

# 2. 検索

# 3. 削除

# 4. session_idが存在しない場合の処理

# 5. セッションの作成時に関連するクライアントとユーザーが正しく設定されること

# 6. セッションの削除が正しく行われること

# 7. セッションの更新時間が正しく更新されること

# 8. セッションの削除が正しく行われること

# 9. ユーザーが削除された場合、関連するセッションも削除されること

# 10. クライアントが削除された場合、関連するセッションも削除されること


# tokenのCRUDテスト
# 1. 作成

# 2. 検索

# 3. 更新

# 4. 削除
