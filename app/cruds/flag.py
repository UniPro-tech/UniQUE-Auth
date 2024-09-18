from sqlalchemy.orm import Session
from ..schemas import (
    Flag as FlagSchema,
    CreateFlag as CreateFlagSchema
)
from ..models import (
    Flag as FlagModel,
    User as UserModel,
)


async def get_flag_by_id(db: Session, flag_id: int):
    role = db.query(FlagModel).filter(FlagModel.id == flag_id).first()
    return FlagSchema.model_validate(role) if role else None


async def get_flag_by_name(db: Session, name: str):
    role = db.query(FlagModel).filter(FlagModel.name == name).first()
    return FlagSchema.model_validate(role) if role else None


async def create_flag(db: Session, flag: CreateFlagSchema):
    flag = FlagModel(**flag.model_dump())
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return FlagSchema.model_validate(flag)


async def update_flag(db: Session, flag_id: int, flag: CreateFlagSchema):
    flag = db.query(FlagModel).filter(FlagModel.id == flag_id).first()
    if flag:
        flag.update(**flag.model_dump())
        db.commit()
        db.refresh(flag)
        return FlagSchema.model_validate(flag)
    return None


async def delete_flag(db: Session, flag_id: int):
    flag = db.query(FlagModel).filter(FlagModel.id == flag_id).first()
    if flag:
        db.delete(flag)
        db.commit()
        return FlagSchema.model_validate(flag)
    return None


async def add_user_to_flag(db: Session, flag_id: int, user_id: int):
    flag = db.query(FlagModel).filter(FlagModel.id == flag_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if flag and user:
        flag.users.append(user)
        db.commit()
        db.refresh(flag)
        return FlagSchema.model_validate(flag)
    return None


async def remove_user_from_flag(db: Session, flag_id: int, user_id: int):
    flag = db.query(FlagModel).filter(FlagModel.id == flag_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if flag and user:
        flag.users.remove(user)
        db.commit()
        db.refresh(flag)
        return FlagSchema.model_validate(flag)
    return None


async def add_admin_user_to_flag(db: Session, flag_id: int, user_id: int):
    flag = db.query(FlagModel).filter(FlagModel.id == flag_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if flag and user:
        flag.admin_users.append(user)
        db.commit()
        db.refresh(flag)
        return FlagSchema.model_validate(flag)
    return None


async def remove_admin_user_from_flag(db: Session, flag_id: int, user_id: int):
    flag = db.query(FlagModel).filter(FlagModel.id == flag_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if flag and user:
        flag.admin_users.remove(user)
        db.commit()
        db.refresh(flag)
        return FlagSchema.model_validate(flag)
    return None
