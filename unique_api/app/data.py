# テスト用のデータを注入する
from sqlalchemy.orm import Session
from unique_api.app.model import Users, Apps, RedirectUris, Roles
from unique_api.app.model.intermediate import UserRole
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
    user = db.query(Users).first()
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

    # ロールの作成 (存在しない場合のみ)
    role = db.query(Roles).first()
    if not role:
        role = Roles(
            custom_id="admin",
            name="admin",
            permission=(
                (1 << 0)
                | (1 << 1)
                | (1 << 2)
                | (1 << 3)
                | (1 << 4)
                | (1 << 8)
                | (1 << 9)
                | (1 << 10)
                | (1 << 11)
                | (1 << 12)
                | (1 << 16)
                | (1 << 18)
                | (1 << 19)
                | (1 << 20)
                | (1 << 24)
                | (1 << 25)
                | (1 << 26)
                | (1 << 27)
            ),
        )
        db.add(role)
        db.flush()  # ロールを先に保存してIDを取得
        # RoleBindingの作成
        binding = UserRole(user_id=user.id, role_id=role.id)
        db.add(binding)
        db.flush()

    db.commit()  # リダイレクトURIを保存
    # テストユーザーで認可する際のテストURLを生成
    print(
        f"http://localhost:8000/auth?response_type=code&scope=openid+profile+email&client_id={app.id}&state=af0ifjsldkj&redirect_uri={redirect_uri.uri}"
    )
