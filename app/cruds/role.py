from ..schemas import (
    Role as RoleSchema,
    CreateRole as CreateRoleSchema
)
from ..models import Role as RoleModel


async def get_role_by_name(db, name: str):
    role = db.query(RoleModel).filter(RoleModel.name == name).first()
    return RoleSchema.model_validate(role) if role else None


async def get_role_by_id(db, role_id: int):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    return RoleSchema.model_validate(role) if role else None


async def create_role(db, role: CreateRoleSchema):
    role = RoleModel(**role.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return RoleSchema.model_validate(role)


async def update_role(db, role_id: int, role: CreateRoleSchema):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if role:
        role.update(**role.model_dump())
        db.commit()
        db.refresh(role)
        return RoleSchema.model_validate(role)
    return None


async def delete_role(db, role_id: int):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if role:
        db.delete(role)
        db.commit()
        return RoleSchema.model_validate(role)
    return None
