# テスト用のデータを注入する
from sqlalchemy.orm import Session
from unique_api.app.model import User, App, Email, RedirectURI
from datetime import datetime
import hashlib


def create_test_data(db: Session):
    # アプリケーションの作成
    app = App(
        client_id="admin_app",
        client_secret="password",
        name="アドミンアプリケーション",
        created_at=datetime.now(),
        invalid=False,
    )
    db.add(app)
    db.flush()  # アプリケーションを先に保存してIDを取得

    # リダイレクトURIの作成
    redirect_uri = RedirectURI(
        app_id=app.id, uri="https://example.com/callback", created_at=datetime.now()
    )
    db.add(redirect_uri)

    user = User(
        name="admin",
        passwd_hash=hashlib.sha256("admin".encode()).hexdigest(),
        icon_uri="https://example.com/icon.png",
        created_at=datetime.now(),
        invalid=False,
    )
    db.add(user)
    db.flush()  # ユーザーを先に保存してIDを取得

    email = Email(user_id=user.id, email="admin@example.com", verified=True)
    db.add(email)
    db.commit()  # リダイレクトURIを保存
    # テストユーザーで認可する際のテストURLを生成
    print(
        f"http://localhost:8000/auth?response_type=code&scope=openid+profile+email&client_id={app.client_id}&state=af0ifjsldkj&redirect_uri={redirect_uri.uri}"
    )
