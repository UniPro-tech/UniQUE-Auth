from ..models import User as UserModel
from ..schemas import User as UserSchema
from ..schemas import CreateUser as CreateUserSchema


async def get_user_by_email(db, email):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    return UserSchema.model_validate(user) if user else None


async def get_user_by_id(db, user_id):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    return UserSchema.model_validate(user) if user else None


async def get_users(db, skip: int = 0, limit: int = 100):
    # WARNING: この関数を使用するユーザーは制限すること。
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return [UserSchema.model_validate(user) for user in users]


async def create_user(db, user: CreateUserSchema):
    user = UserModel(**user.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserSchema.model_validate(user)


async def update_user(db, user_id: int, user: CreateUserSchema):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        user.update(**user.model_dump())
        db.commit()
        db.refresh(user)
        return UserSchema.model_validate(user)
    return None


async def delete_user(db, user_id: int):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return UserSchema.model_validate(user)
    return None
