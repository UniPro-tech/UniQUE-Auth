from sqlalchemy.orm import Session
from ..schemas import (
    Flug as FlugSchema,
    CreateFlug as CreateFlugSchema
)
from ..models import (
    Flug as FlugModel,
    User as UserModel,
)


async def get_flug_by_id(db: Session, flug_id: int):
    role = db.query(FlugModel).filter(FlugModel.id == flug_id).first()
    return FlugSchema.model_validate(role) if role else None


async def get_flug_by_name(db: Session, name: str):
    role = db.query(FlugModel).filter(FlugModel.name == name).first()
    return FlugSchema.model_validate(role) if role else None


async def create_flug(db: Session, flug: CreateFlugSchema):
    flug = FlugModel(**flug.model_dump())
    db.add(flug)
    db.commit()
    db.refresh(flug)
    return FlugSchema.model_validate(flug)


async def update_flug(db: Session, flug_id: int, flug: CreateFlugSchema):
    flug = db.query(FlugModel).filter(FlugModel.id == flug_id).first()
    if flug:
        flug.update(**flug.model_dump())
        db.commit()
        db.refresh(flug)
        return FlugSchema.model_validate(flug)
    return None


async def delete_flug(db: Session, flug_id: int):
    flug = db.query(FlugModel).filter(FlugModel.id == flug_id).first()
    if flug:
        db.delete(flug)
        db.commit()
        return FlugSchema.model_validate(flug)
    return None


async def add_user_to_flug(db: Session, flug_id: int, user_id: int):
    flug = db.query(FlugModel).filter(FlugModel.id == flug_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if flug and user:
        flug.users.append(user)
        db.commit()
        db.refresh(flug)
        return FlugSchema.model_validate(flug)
    return None


async def remove_user_from_flug(db: Session, flug_id: int, user_id: int):
    flug = db.query(FlugModel).filter(FlugModel.id == flug_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if flug and user:
        flug.users.remove(user)
        db.commit()
        db.refresh(flug)
        return FlugSchema.model_validate(flug)
    return None
