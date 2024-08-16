from sqlalchemy.orm import Session
from ..schemas import (
    App as AppSchema,
    CreateApp as CreateAppSchema
)
from ..models import App as AppModel


async def get_app_by_name(db: Session, name: str):
    app = db.query(AppModel).filter(AppModel.name == name).first()
    return AppSchema.model_validate(app) if app else None


async def get_app_by_id(db: Session, app_id: int):
    app = db.query(AppModel).filter(AppModel.id == app_id).first()
    return AppSchema.model_validate(app) if app else None


async def create_app(db: Session, app: CreateAppSchema):
    app = AppModel(**app.model_dump())
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
