from sqlalchemy.orm import Session
from ..models import User as UserModel
import hashlib
from ..schemas import (
    User as UserSchema,
    CreateUser as CreateUserSchema,
    Me as MeSchema

)


async def get_user_by_email(db: Session, email: str) -> UserSchema:
    user = db.query(UserModel).filter(UserModel.email == email).first()
    return UserSchema.model_validate(user) if user else None


async def get_user_by_name(db: Session, name: str) -> UserSchema:
    user = db.query(UserModel).filter(UserModel.name == name).first()
    return UserSchema.model_validate(user) if user else None


async def get_user_by_id(db: Session, user_id: int):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    return UserSchema.model_validate(user) if user else None


async def get_users(db: Session, skip: int = 0, limit: int = 100):
    # WARNING: この関数を使用するユーザーは制限すること。
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return [UserSchema.model_validate(user) for user in users]


async def create_user(db: Session, user: CreateUserSchema) -> MeSchema:
    user = UserModel(**user.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeSchema.model_validate(user)


async def update_user(db: Session, user_id: int, user: CreateUserSchema):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        user.update(**user.model_dump())
        db.commit()
        db.refresh(user)
        return UserSchema.model_validate(user)
    return None


async def delete_user(db: Session, user_id: int):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return UserSchema.model_validate(user)
    return None


async def get_user_by_email_passwd(
        db: Session, email: str, passwd: str
        ) -> bool:
    user: CreateUserSchema = (
        db.query(UserModel)
        .filter(UserModel.email == email)
        .first()
    )
    if not user:
        return False
    hashed_passwd = hashlib.sha256(passwd.encode()).hexdigest()
    return user.hash_password == hashed_passwd if user else False
