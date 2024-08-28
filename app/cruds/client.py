from sqlalchemy.orm import Session
from ..schemas import (
    UserClient as UserClientSchema,
    AppClient as AppClientSchema,
)
from ..models import (
    Client as ClientModel,
    User as UserModel,
    App as AppModel,
)


async def get_client_by_id(db: Session, client_id: int):
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    return UserClientSchema.model_validate(client) if client else None


async def create_user_client(
        db: Session, client: AppClientSchema
        ) -> UserClientSchema:
    client = ClientModel(**client.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return UserClientSchema.model_validate(client)


async def update_user_client(db: Session, client: UserClientSchema):
    existing_client = db.query(ClientModel).filter(ClientModel.id == client.id).first()
    if existing_client:
        user = db.query(UserModel).filter(UserModel.id == client.user).first()
        if not user:
            return None
        existing_client.update(**client.model_dump(), user=user)
        db.commit()
        db.refresh(existing_client)
        return UserClientSchema.model_validate(existing_client)
    return None


async def create_app_client(db: Session, client: AppClientSchema):
    app = db.query(AppModel).filter(AppModel.id == client.app).first()
    if not app:
        return None
    client = ClientModel(**client.model_dump(), app=app)
    db.add(client)
    db.commit()
    db.refresh(client)
    return AppClientSchema.model_validate(client)


async def update_app_client(db: Session, client: AppClientSchema):
    existing_client = db.query(ClientModel).filter(ClientModel.id == client.id).first()
    if existing_client:
        app = db.query(AppModel).filter(AppModel.id == client.app).first()
        if not app:
            return None
        existing_client.update(**client.model_dump(), app=app)
        db.commit()
        db.refresh(existing_client)
        return AppClientSchema.model_validate(existing_client)
    return None
