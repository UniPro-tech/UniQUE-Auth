import os
import sys
sys.path.append("/home/sibainu/Project/UniQUE-API")

from app.cruds.session import (
    create_session,
    get_session_by_id,
    delete_session_by_id,
)
from app.cruds.client import (
    create_client,
    get_client_by_id,
    update_client,
    delete_client_by_id,
    create_redirect_uri,
    delete_redirect_uri,
)
from app.cruds.user import (
    create_user,
    get_user_by_id,
    get_user_by_email
)
from app.models import Client, User
from app.database import Base, engine, SessionLocal, get_db
import hashlib


def hash_password(password: str) -> str:
    # パスワードをUTF-8でエンコードし、SHA-256でハッシュ化
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed


if __name__ == "__main__":


    session = next(get_db())
    # データベースの初期化

    # UserとClientのテーブルを作成
    new_client = create_client(
        session,
        name="test",
        client_id="test_client",
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
    # 例：client_objとuser_objを取得（または作成済みのオブジェクトを使用）
    client_obj = session.query(Client).first()  # 例として最初のClientを取得
    user_obj = session.query(User).first()  # 例として最初のUserを取得

    # 新しいSessionレコードを作成
    session_obj = create_session(
        session,
        session_id="session_001",
        client_obj=client_obj,
        user_obj=user_obj,
    )
    print("Created Session:", session_obj)

    # session_idで検索
    found = get_session_by_id(session, "session_001")
    print("Found Session:", found)

    # 削除
    if delete_session_by_id(session, "session_001"):
        print("Session 'session_001' deleted successfully.")
    else:
        print("Session 'session_001' not found.")
