from sqlalchemy.orm import Session
from ..schemas import (
    App as AppSchema,
    CreateApp as CreateAppSchema,
    Me as MeSchema,
)
from ..models import (
    App as AppModel,
    User as UserModel,
)


async def get_app_by_name(db: Session, name: str):
    app = db.query(AppModel).filter(AppModel.name == name).first()
    return AppSchema.model_validate(app) if app else None


async def get_app_by_id(db: Session, app_id: int):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    return AppSchema.model_validate(app) if app else None


async def create_app(db: Session, app: CreateAppSchema, user: MeSchema):
    app = AppModel(**app.model_dump())
    app.admin_users = user.id
    db.add(app)
    db.commit()
    db.refresh(app)
    return AppSchema.model_validate(app)


async def update_app(db: Session, app_id: int, app: CreateAppSchema):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    if app:
        app.update(**app.model_dump())
        db.commit()
        db.refresh(app)
        return AppSchema.model_validate(app)
    return None


async def delete_app(db: Session, app_id: int):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    if app:
        db.delete(app)
        db.commit()
        return AppSchema.model_validate(app)
    return None


def add_user_to_app(db: Session, app_id: int, user_id: int):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if app and user:
        app.users.append(user)
        db.commit()
        db.refresh(app)
    return app


def remove_user_from_app(db: Session, app_id: int, user_id: int):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if app and user:
        app.users.remove(user)
        db.commit()
        db.refresh(app)
    return app


def add_admin_user_to_app(db: Session, app_id: int, user_id: int):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if app and user:
        app.admin_users.append(user)
        db.commit()
        db.refresh(app)
    return app


def remove_admin_user_from_app(db: Session, app_id: int, user_id: int):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if app and user:
        app.admin_users.remove(user)
        db.commit()
        db.refresh(app)
    return app
