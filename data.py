# テスト用のデータを注入する
from sqlalchemy.orm import Session
from model import User, App, Email, RedirectURI, Auth, Consent, OIDCTokens, Token, Session as UserSession
from datetime import datetime
from uuid import uuid4


def create_test_data(db: Session):

    # アプリケーションの作成
    app = App(
        client_id=f"test_client_id_{uuid4()}",
        client_secret="test_client_secret",
        name="Test Application",
        created_at=datetime.now(),
        invalid=False
    )
    db.add(app)
    db.flush()  # アプリケーションを先に保存してIDを取得

    # リダイレクトURIの作成
    redirect_uri = RedirectURI(
        app_id=app.id,
        uri="https://example.com/callback",
        created_at=datetime.now()
    )
    db.add(redirect_uri)
    db.commit()  # リダイレクトURIを保存