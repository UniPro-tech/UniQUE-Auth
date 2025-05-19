import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "/home/sibainu/Project/UniQUE-API")))

from app.cruds.client import (
    create_client,
    get_client_by_client_id,
    delete_client_by_client_id,
)
from app.cruds.app import (
    create_app,
    get_app_by_name,
    get_app_by_id,
    create_redirect_uri,
    get_redirect_uris_by_app_id,
    delete_redirect_uri,
)
from app.cruds.user import (
    create_user,
    get_user_by_id,
    get_user_by_email
)
from app.models import App, User
from app.database import Base, engine, SessionLocal, get_db
import hashlib


def hash_password(password: str) -> str:
    # パスワードをUTF-8でエンコードし、SHA-256でハッシュ化
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    session = next(get_db())
    Base.metadata.create_all(bind=engine)

    # UserとAppのテーブルを作成
    new_app = create_app(
        session,
        name="Test App",
        scope="openid profile email",
        client_type="confidential",
        grant_types="authorization_code",
        response_types="code",
        token_endpoint_auth_method="client_secret_basic",
    )
    new_user = create_user(
        session,
        name="test",
        email="test",
        hash_password=hash_password("test"),
    )
    test_user = get_user_by_email(session, "test")
    if test_user:
        print("User found:", test_user)
    else:
        print("User not found.")
    # 例：app_objとuser_objを取得（または作成済みのオブジェクトを使用）
    app_obj = session.query(App).first()  # 例として最初のAppを取得
    user_obj = session.query(User).first()  # 例として最初のUserを取得

    # 新しいClientレコードを作成
    client = create_client(
        session,
        client_id="client_001",
        client_secret="super_secret_value",
        app_obj=app_obj,
        user_obj=user_obj,
#        logo_uri="https://example.com/logo.png",
        client_uri="https://example.com",
    )
    print("Created Client:", client)

    # client_idで検索
    found = get_client_by_client_id(session, "client_001")
    print("Found Client:", found)

    # 削除
    if delete_client_by_client_id(session, "client_001"):
        print("Client 'client_001' deleted successfully.")
    else:
        print("Client 'client_001' not found.")
