# テスト用のデータを注入する
from sqlalchemy.orm import Session
from unique_api.app.model import Member, User, App, RedirectURI
from datetime import datetime
import hashlib


def create_test_data(db: Session):
    # アプリケーションの作成 (存在しない場合のみ)
    app = db.query(App).filter_by(client_id="admin_app").first()
    if not app:
        app = App(
            client_id="admin_app",
            client_secret="password",
            name="アドミンアプリケーション",
            created_at=datetime.now(),
            is_enable=False,
        )
        db.add(app)
        db.flush()  # アプリケーションを先に保存してIDを取得

    # リダイレクトURIの作成 (存在しない場合のみ)
    redirect_uri = (
        db.query(RedirectURI)
        .filter_by(uri="https://example.com/callback", app_id=app.id)
        .first()
    )
    if not redirect_uri:
        redirect_uri = RedirectURI(
            app_id=app.id, uri="https://example.com/callback", created_at=datetime.now()
        )
        db.add(redirect_uri)

    # メンバーの作成 (存在しない場合のみ)
    member = db.query(Member).filter_by(custom_id="admin").first()
    if not member:
        member = Member(
            custom_id="admin",
            name="admin",
            email="admin@example.com",
            external_email="admin@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            joined_at=datetime.now(),
            is_enable=True,
            period="00",
            system=False,
        )
        db.add(member)

    # ユーザーの作成 (存在しない場合のみ)
    user = db.query(User).filter_by(custom_id="admin").first()
    if not user:
        user = User(
            custom_id="admin",
            password_hash=hashlib.sha256("admin".encode()).hexdigest(),
            created_at=datetime.now(),
            is_enable=False,
        )
        db.add(user)
        db.flush()  # ユーザーを先に保存してIDを取得

    # TODO: ユーザーのメールアドレスの登録ロジックを変更
    # db.add(email)
    db.commit()  # リダイレクトURIを保存
    # テストユーザーで認可する際のテストURLを生成
    print(
        f"http://localhost:8000/auth?response_type=code&scope=openid+profile+email&client_id={app.client_id}&state=af0ifjsldkj&redirect_uri={redirect_uri.uri}"
    )
