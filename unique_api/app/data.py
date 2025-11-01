# テスト用のデータを注入する
from sqlalchemy.orm import Session
from unique_api.app.model import Users, Apps, RedirectUris
import hashlib


def create_test_data(db: Session):
    # アプリケーションの作成 (存在しない場合のみ)
    app = db.query(Apps).filter_by(name="admin_app").first()
    if not app:
        app = Apps(
            client_secret="password",
            name="admin_app",
            is_enable=False,
        )
        db.add(app)
        db.flush()  # アプリケーションを先に保存してIDを取得

    # リダイレクトURIの作成 (存在しない場合のみ)
    redirect_uri = (
        db.query(RedirectUris)
        .filter_by(uri="https://example.com/callback", app_id=app.id)
        .first()
    )
    if not redirect_uri:
        redirect_uri = RedirectUris(app_id=app.id, uri="https://example.com/callback")
        db.add(redirect_uri)

    # ユーザーの作成 (存在しない場合のみ)
    user = db.query(Users).filter_by(custom_id="admin").first()
    if not user:
        user = Users(
            custom_id="admin",
            password_hash=hashlib.sha256("admin".encode()).hexdigest(),
            name="管理者",
            email="admin@uniproject.jp",
            external_email="admin@uniproject.jp",
            is_enable=True,
            is_system=True,
            period="00",
        )
        db.add(user)
        db.flush()  # ユーザーを先に保存してIDを取得

    db.commit()  # リダイレクトURIを保存
    # テストユーザーで認可する際のテストURLを生成
    print(
        f"http://localhost:8000/auth?response_type=code&scope=openid+profile+email&client_id={app.id}&state=af0ifjsldkj&redirect_uri={redirect_uri.uri}"
    )
