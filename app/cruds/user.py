from app.models.user import User
from sqlalchemy.orm import Session


def create_user(session: Session, name: str, email: str, hash_password: str):
    new_user = User(
        name=name,
        email=email,
        hash_password=hash_password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def get_user_by_id(session: Session, user_id: int):
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str):
    return session.query(User).filter(User.email == email).first()


def get_all_users(session: Session):
    return session.query(User).all()


def update_user(session: Session, user_id: int, **kwargs):
    user = get_user_by_id(session, user_id)
    if not user:
        return None
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int):
    user = get_user_by_id(session, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True

# 
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.models import User  # Userモデルのインポート
# from app.database import Base  # Baseのインポート
# 
# # データベースエンジンの作成
# engine = create_engine("sqlite:///example.db", echo=True)
# SessionLocal = sessionmaker(bind=engine)
# session = SessionLocal()
# 
# # テーブルの作成
# Base.metadata.create_all(bind=engine)
# 
# # ユーザーの作成
# user = create_user(session, name="Alice", email="alice@example.com", hash_password="hashed_pw")
# 
# # ユーザーの取得
# retrieved_user = get_user_by_id(session, user.id)
# 
# # ユーザーの更新
# updated_user = update_user(session, user.id, name="Alice Smith")
# 
# # ユーザーの削除
# delete_success = delete_user(session, user.id)
# 
# # セッションのクローズ
# session.close()
