import hashlib
from sqlalchemy.orm import Session
from .schemas import UserCreate, User
from .models import User as UserModel


def get_user(db: Session, user_id: int) -> User:
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_user_by_userid(db: Session, user_id: str) -> User:
    return db.query(UserModel).filter(UserModel.user_id == user_id).first()


def get_user_by_email_password(
            db: Session, email: str, password: str
        ) -> User:
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return (db.query(UserModel)
            .filter(UserModel.email == email,
                    UserModel.hashed_password == hashed_password
                    )
            .first())


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = UserModel(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
