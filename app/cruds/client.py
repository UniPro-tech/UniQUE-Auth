from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo


# 例：Clientテーブルへのレコード作成
def create_client(
    session: Session,
    client_id: str,
    client_secret: str,
    app_obj,    # Appモデルのインスタンス
    user_obj,   # Userモデルのインスタンス
    client_type: str = "confidential",
    grant_types: str = "authorization_code",
    response_types: str = "code",
    token_endpoint_auth_method: str = "client_secret_basic",
    logo_uri: str = None,
    client_uri: str = None,
    tos_uri: str = None,
    policy_uri: str = None,
):
    new_client = Client(
        client_id=client_id,
        client_secret=client_secret,
        client_type=client_type,
        grant_types=grant_types,
        response_types=response_types,
        token_endpoint_auth_method=token_endpoint_auth_method,
        logo_uri=logo_uri,
        client_uri=client_uri,
        tos_uri=tos_uri,
        policy_uri=policy_uri,
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC")),
        app=app_obj,
        user=user_obj,
    )
    session.add(new_client)
    session.commit()          # データベースに反映
    session.refresh(new_client)  # 新しいレコードを再読み込み
    return new_client


# 例：client_idをキーに検索する
def get_client_by_client_id(session: Session, client_id: str):
    return session.query(Client).filter(Client.client_id == client_id).first()


# 例：client_idをキーにレコードを削除する
def delete_client_by_client_id(session: Session, client_id: str):
    client = get_client_by_client_id(session, client_id)
    if client:
        session.delete(client)
        session.commit()
        return True
    return False



# # ----- 使用例 -----
# if __name__ == "__main__":
#     from sqlalchemy import create_engine
#     from sqlalchemy.orm import sessionmaker
# 
#     # 例としてSQLiteのDBに接続（実際の環境に合わせてURLを変更してください）
#     engine = create_engine("sqlite:///example.db", echo=True)
#     SessionLocal = sessionmaker(bind=engine)
#     session = SessionLocal()
# 
#     # ※事前にAppおよびUserテーブルに対応するレコードが存在していることが前提です
#     # 例：app_objとuser_objを取得（または作成済みのオブジェクトを使用）
#     app_obj = session.query(App).first()  # 例として最初のAppを取得
#     user_obj = session.query(User).first()  # 例として最初のUserを取得
# 
#     # 新しいClientレコードを作成
#     client = create_client(
#         session,
#         client_id="client_001",
#         client_secret="super_secret_value",
#         app_obj=app_obj,
#         user_obj=user_obj,
#         logo_uri="https://example.com/logo.png",
#         client_uri="https://example.com",
#     )
#     print("Created Client:", client)
# 
#     # client_idで検索
#     found = get_client_by_client_id(session, "client_001")
#     print("Found Client:", found)
# 
#     # 削除
#     if delete_client_by_client_id(session, "client_001"):
#         print("Client 'client_001' deleted successfully.")
#     else:
#         print("Client 'client_001' not found.")
