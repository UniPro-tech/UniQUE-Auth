from ..schemas import (
    Role as RoleSchema,
    CreateRole as CreateRoleSchema
)
from sqlalchemy.orm import Session
from ..models import (
    Role as RoleModel,
    User as UserModel
)


async def get_role_by_name(db: Session, name: str):
    role = db.query(RoleModel).filter(RoleModel.name == name).first()
    return RoleSchema.model_validate(role) if role else None


async def get_role_by_id(db: Session, role_id: int):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    return RoleSchema.model_validate(role) if role else None


async def create_role(db: Session, role: CreateRoleSchema):
    role = RoleModel(**role.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleSchema.model_validate(role)


async def update_role(db: Session, role_id: int, role: CreateRoleSchema):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if role:
        role.update(**role.model_dump())
        db.commit()
        db.refresh(role)
        return RoleSchema.model_validate(role)
    return None


async def delete_role(db: Session, role_id: int):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if role:
        db.delete(role)
        db.commit()
        return RoleSchema.model_validate(role)
    return None


async def add_user_to_role(db: Session, role_id: int, user_id: int):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if role and user:
        role.users.append(user)
        db.commit()
        db.refresh(role)
        return RoleSchema.model_validate(role)
    return None


async def remove_user_from_role(db: Session, role_id: int, user_id: int):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if role and user:
        role.users.remove(user)
        db.commit()
        db.refresh(role)
        return RoleSchema.model_validate(role)
    return None