from models.user import User
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


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    user = session.query(User).filter(User.email == email).first()
    return user


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


def delete_user_by_id(session: Session, id: int):
    user = get_user_by_id(session, id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True
