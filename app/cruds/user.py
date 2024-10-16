from sqlalchemy.orm import Session
from ..models import User as UserModel
import hashlib
from ..schemas import (
    User as UserSchema,
    CreateUser as CreateUserSchema,
    UpdataMe as UpdataMeSchema
)


async def get_user_by_email(
                session: Session, email: str
            ) -> UserSchema | None:
    user = (
        session.query(UserModel)
        .filter(UserModel.email == email)
        .first()
    )
    return user if user else None


async def get_user_by_name(
                session: Session, name: str
            ) -> UserModel | None:
    user = (
        session.query(UserModel)
        .filter(UserModel.name == name)
        .first()
    )
    return user if user else None


async def get_user_by_id(
                session: Session, user_id: int
            ) -> UserSchema | None:
    user = (
        session.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )
    return user if user else None


async def get_users(
                session: Session,
                skip: int = 0, limit: int = 100
            ) -> list[UserSchema]:
    # WARNING: この関数を使用するユーザーは制限すること。
    users = (
        session.query(UserModel)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [UserSchema.model_validate(user) for user in users]


async def create_user(
                session: Session, user: CreateUserSchema
            ) -> UserModel:
    user = UserModel(**user.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def update_user(
                session: Session, user: UserModel,
                updates: UpdataMeSchema
            ) -> UserModel:
    update_data = updates.model_dump()
    for key, value in update_data.items():
        setattr(user, key, value)
    session.commit()
    return user


async def delete_user(
                session: Session, user: UserModel
            ) -> UserModel:
    session.delete(user)
    session.commit()
    return user


async def get_user_by_email_passwd(
                session: Session, email: str, passwd: str
            ) -> bool:
    user: CreateUserSchema = (
        session.query(UserModel)
        .filter(UserModel.email == email)
        .first()
    )
    if not user:
        return None
    if user.hash_password == hashlib.sha256(passwd.encode()).hexdigest():
        return user
    return None
