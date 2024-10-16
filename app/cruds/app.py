from sqlalchemy.orm import Session
from ..schemas import (
    App as AppSchema,
    CreateApp as CreateAppSchema,
)
from ..models import (
    App as AppModel,
    User as UserModel,
)


async def get_app_by_name(
                session: Session, name: str
            ) -> AppModel | None:
    app = (
        session.query(AppModel)
        .filter(AppModel.name == name)
        .first()
    )
    return AppSchema.model_validate(app) if app else None


async def get_app_by_id(
                session: Session, app_id: int
            ) -> AppModel | None:
    app = (
        session.query(AppModel)
        .filter(AppModel.id == app_id)
        .first()
    )
    return AppSchema.model_validate(app) if app else None


async def get_apps(
                session: Session, skip: int = 0, limit: int = 100
            ) -> list[AppModel]:
    apps = session.query(AppModel).offset(skip).limit(limit).all()
    return [AppSchema.model_validate(app) for app in apps]


async def create_app(
                session: Session,
                app: CreateAppSchema, user: UserModel
            ) -> AppModel:
    app = AppModel(**app.model_dump())

    app.admin_users.append(user)
    session.add(app)
    session.commit()
    session.refresh(app)
    return app


async def update_app(
                session: Session,
                app: AppModel,
                updates: CreateAppSchema
            ) -> AppModel:
    update_data = updates.model_dump()
    for key, value in update_data.items():
        setattr(app, key, value)
    session.commit()
    return app


async def delete_app(
                session: Session, app_id: int
            ) -> AppModel | None:
    app = session.query(AppModel).filter(AppModel.id == app_id).first()
    if app:
        session.delete(app)
        session.commit()
        return app
    return None


async def add_user_to_app(
                session: Session,
                app: AppModel, user: UserModel
            ) -> AppModel:
    app.users.append(user)
    session.commit()
    return app


async def remove_user_from_app(
                session: Session,
                app: AppModel, user: UserModel
            ) -> AppModel:
    if app and user:
        app.users.remove(user)
        session.commit()
    return app


async def add_admin_user_to_app(
                session: Session,
                app: AppModel, user: UserModel
            ) -> AppModel:
    if app and user:
        app.admin_users.append(user)
        session.commit()
    return app


async def remove_admin_user_from_app(
                session: Session,
                app: AppModel, user: UserModel
            ):
    if app and user:
        app.admin_users.remove(user)
        session.commit()
    return app
