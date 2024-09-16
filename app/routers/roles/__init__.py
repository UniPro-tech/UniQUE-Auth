from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...cruds.token import verify_token
from ...schemas import (
    Role as RoleSchema,
    CreateRole as CreateRoleSchema,
    UpdateRole as UpdateRoleSchema,
    Me as MeSchema,
)
from ...cruds.role import (
    get_role_by_id,
    create_role,
    update_role,
    delete_role,
    add_user_to_role,
)

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=RoleSchema)
async def create_roles(
            role: CreateRoleSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    new_role: RoleSchema = await create_role(db=db, role=role)
    new_role: RoleSchema = await add_user_to_role(db, new_role.id, user.id)
    return new_role


@router.get("/{role_id}", response_model=RoleSchema)
async def read_roles(
            role_id: int,
            db: Session = Depends(get_db)
        ):
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/{role_id}", response_model=RoleSchema)
async def edit_roles(
            role_id: int,
            role: UpdateRoleSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    # TODO: 権限周りの処理は後ほど記述
    role = await update_role(db, role_id, role)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.delete("/{role_id}", response_model=RoleSchema)
async def delete_roles(
            role_id: int,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    # TODO: 権限周りの処理は後ほど記述
    role = await delete_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role
