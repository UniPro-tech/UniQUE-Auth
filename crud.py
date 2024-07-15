from sqlalchemy.orm import Session
import hashlib
import re

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_email(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()

def get_user_by_email_password(db: Session, email: str, password: str):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return db.query(models.User).filter(models.User.email == email, models.User.hashed_password == hashed_password).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

