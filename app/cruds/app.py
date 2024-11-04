from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import (
    App as AppModel,
    User as UserModel,
    Log as LogModel
)
from app.schemas import App as AppSchema


async def get_app_by_name(
                session: Session, name: str
            ) -> AppModel | None:
    app = (
        session.scalar(
            select(AppModel)
            .where(AppModel.name == name)
        )
    )
    return app


async def get_app_by_id(
                session: Session, app_id: int
            ) -> AppModel | None:
    app = (
        session.scalar(
            select(AppModel)
            .where(AppModel.id == app_id)
        )
    )
    return app


async def get_apps(
                session: Session, skip: int = 0, limit: int = 100
            ) -> list[AppModel]:
    apps = session.scalar(
        select(AppModel)
        .offset(skip)
        .limit(limit)
    )
    return apps


async def create_app(
                session: Session,
                app: AppModel,
                admin_user: UserModel
            ) -> AppModel:
    log = LogModel(
        action_type="create",
        action_entity="user",
        description=f"Create app {app.name} by {admin_user.name}",
        user=admin_user
    )
    app = AppModel(
        name=app.name,
        admin_users=[admin_user],
        logs=[log]
    )
    session.add(app)
    session.commit()
    session.refresh(app)
    return app


async def update_app(
                session: Session,
                app: AppModel,
                updates: AppSchema
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
