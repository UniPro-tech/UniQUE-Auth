import hashlib
import json
import time
from sqlalchemy.orm import Session
import models
import schemas


def get_user(db: Session, user_id: int) -> schemas.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> schemas.User:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_userid(db: Session, user_id: str) -> schemas.User:
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email_password(
            db: Session, email: str, password: str
        ) -> schemas.User:
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return (db.query(models.User)
            .filter(models.User.email == email,
                    models.User.hashed_password == hashed_password)
            .first())


def create_user(db: Session, user: schemas.UserCreate) -> schemas.User:
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = models.User(
        email=user.email, hashed_password=hashed_password,
        name=user.name, user_id=user.user_id, created_at=int(time.time()))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> json:
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return {"message": "User deleted"}
