from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas import (
    CreateFlag as CreateFlagSchema,
    UpdataFlag as UpdataFlagSchema
)
from app.models import (
    Flag as FlagModel,
    User as UserModel,
)


async def get_flag_by_id(
                session: Session, flag_id: int
            ) -> FlagModel | None:
    role = (
        session.scalar(
            select(FlagModel)
            .where(FlagModel.id == flag_id)
        )
    )
    return role if role else None


async def get_flag_by_name(
                session: Session, name: str
            ) -> FlagModel | None:
    role = (
        session.scalar(
            select(FlagModel)
            .where(FlagModel.name == name)
        )
    )
    return role if role else None


async def get_flags(
                session: Session, skip: int = 0, limit: int = 100
            ) -> list[FlagModel]:
    flags = session.scalar(
        select(FlagModel)
        .offset(skip)
        .limit(limit)
    )
    return flags


async def create_flag(
                session: Session, flag: CreateFlagSchema
            ) -> FlagModel:
    flag = FlagModel(**flag.model_dump())
    session.add(flag)
    session.commit()
    session.refresh(flag)
    return flag


async def update_flag(
                session: Session,
                flag: FlagModel, updates: UpdataFlagSchema
            ) -> FlagModel:
    update_data = updates.model_dump()
    for key, value in update_data.items():
        setattr(flag, key, value)
    session.commit()
    return flag


async def delete_flag(
                session: Session, flag: FlagModel
            ) -> FlagModel:
    session.delete(flag)
    session.commit()
    return flag


async def add_user_to_flag(
                session: Session,
                flag: FlagModel, user: UserModel
            ) -> FlagModel:
    flag.users.append(user)
    session.commit()
    session.refresh(flag)
    return flag


async def remove_user_from_flag(
                session: Session,
                flag: FlagModel, user: UserModel
            ) -> FlagModel:
    flag.users.remove(user)
    session.commit()
    session.refresh(flag)
    return flag
