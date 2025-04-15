from app.cruds.client import (
    create_client,
    get_client_by_client_id,
    delete_client_by_client_id,
)
from app.models import App, User

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # 例としてSQLiteのDBに接続（実際の環境に合わせてURLを変更してください）
    engine = create_engine("sqlite:///:memory:", echo=True)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # ※事前にAppおよびUserテーブルに対応するレコードが存在していることが前提です
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
        logo_uri="https://example.com/logo.png",
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
