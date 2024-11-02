from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.models import (
    User,
    App,
    Role,
    Flag,
    Client,
    Log,
    Token
)
from app.database import Base
from functools import wraps
import itertools

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


role_list = ["admin", "user", "guest"]
flag_list = ["pumpkin", "candy", "witch"]
app_list = ["pumpkin_farm", "candy_factory", "witch's_castle"]


# おばけっぽい名前を生成する関数
def generate_all_ghost_names():
    first_names = ["モヤ", "シャド", "カゲ", "ヒソ", "ササ", "ユラ"]
    last_names = ["ノヒト", "ダマシ", "カラ", "ヤミ", "フユ", "サビ"]

    # 全ての組み合わせを作成
    ghost_names = [first + last for first, last in itertools.product(first_names, last_names)]
    return ghost_names


def create_user(username: str, password: str, session: Session = next(get_db())):
    user = User(
            name=username,
            email=f"{username}@sibainu.tech",
            hash_password=password,
            display_name=username,
        )
    session.add(user)
    session.commit()
    return user


def create_app(name: str, session: Session = next(get_db())):
    app = App(name=name)
    session.add(app)
    session.commit()
    return app


def create_role(name: str, session: Session = next(get_db())):
    role = Role(
            name=name,
            display_name=name,
            description=f"{name} role",
            permission_bit=0,
            is_enabled=True,
            is_deactivated=False,
            sort=0
        )
    session.add(role)
    session.commit()
    return role


def create_flag(name: str, session: Session = next(get_db())):
    flag = Flag(
            name=name,
            display_name=name,
            description=f"{name} flag",
            is_enabled=True,
            can_assign=True
        )
    session.add(flag)
    session.commit()
    return flag


def create_token(client: Client, session: Session = next(get_db())):
    token = Token(
            client=client,
            access_token="access_token",
            refresh_token="refresh_token",
        )
    session.add(token)
    session.commit()
    return token


def create_client(user: User, session: Session = next(get_db())):
    client = Client(
            user=user,
            )
    session.add(client)
    session.commit()
    return client


def user_add_role(user: User, role: Role, session: Session = next(get_db())):
    user.roles.append(role)
    session.commit()
    return user


def user_add_flag(user: User, flag: Flag, session: Session = next(get_db())):
    user.flags.append(flag)
    session.commit()
    return user


def user_add_app(user: User, app: App, session: Session = next(get_db())):
    user.apps.append(app)
    session.commit()
    return user

def user_add_client(user: User, client: Client, session: Session = next(get_db())):
    user.clients.append(client)
    session.commit()
    return user


if __name__ == "__main__":
    session = next(get_db())

    for user in generate_all_ghost_names():
        create_user(user, "password", session)

    for role in role_list:
        create_role(role, session)

    for flag in flag_list:
        create_flag(flag, session)

    for app in app_list:
        create_app(app, session)

    user = session.query(User).all()
    role = session.query(Role).all()
    flag = session.query(Flag).all()
    app = session.query(App).all()

    for u, r in itertools.product(user, role):
        user_add_role(u, r, session)
    
    for u, f in itertools.product(user, flag):
        user_add_flag(u, f, session)
    
    for u, a in itertools.product(user, app):
        user_add_app(u, a, session)
    
    user = session.query(User).first()
    client = create_client(user, session)
    create_token(client, session)
