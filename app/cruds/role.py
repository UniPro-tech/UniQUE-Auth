from sqlalchemy import select
from ..schemas import (
    CreateRole as CreateRoleSchema,
    UpdateRole as UpdateRoleSchema,
)
from sqlalchemy.orm import Session
from ..models import (
    Role as RoleModel,
    User as UserModel
)


async def get_role_by_name(
                session: Session, name: str
            ) -> RoleModel | None:
    role = (
        session.scalar(
            select(RoleModel)
            .where(RoleModel.name == name)
        )
    )
    return role if role else None


async def get_role_by_id(
                session: Session, role_id: int
            ) -> RoleModel | None:
    role = (
        session.scalar(
            select(RoleModel)
            .where(RoleModel.id == role_id)
        )
    )
    return role if role else None


async def get_roles(
                session: Session, skip: int = 0, limit: int = 100
            ) -> list[RoleModel]:
    roles = session.scalar(
        select(RoleModel)
        .offset(skip)
        .limit(limit)
    )
    return roles


async def create_role(
                session: Session, role: CreateRoleSchema
            ) -> RoleModel:
    role = RoleModel(**role.model_dump())
    session.add(role)
    session.commit()
    return role


async def update_role(
                session: Session,
                role: RoleModel, updates: UpdateRoleSchema
            ) -> RoleModel:
    update_data = updates.model_dump()
    for key, value in update_data.items():
        setattr(role, key, value)
    session.commit()
    return role


async def delete_role(
                session: Session, role: int
            ) -> RoleModel:
    session.delete(role)
    session.commit()
    return role


async def add_user_to_role(
                session: Session,
                role: RoleModel, user: UserModel
            ) -> RoleModel:
    role.users.append(user)
    session.commit()
    session.refresh(role)
    return role


async def remove_user_from_role(
                session: Session,
                role: RoleModel, user: UserModel):
    role.users.remove(user)
    session.commit()
    session.refresh(role)
    return role
