from sqlalchemy.orm import Session
from app.schemas import (
    UpdataClient as UpdataClientSchema,
    User as UserSchema,
    App as AppSchema,
)
from ..models import (
    Client as ClientModel,
    User as UserModel,
    App as AppModel,
)


async def get_client_by_id(
                session: Session, client_id: int
            ) -> ClientModel | None:
    client = (
        session.query(ClientModel)
        .filter(ClientModel.id == client_id)
        .first()
    )
    return client if client else None


async def create_client(
            session: Session, user: UserSchema,
            app: AppSchema, user_client=True
        ) -> ClientModel:
    client = ClientModel()
    if user_client:
        client.user = UserModel(**user.model_dump())
    else:
        client.app = AppModel(**app.model_dump())
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


async def update_user_client(
            session: Session,
            client: ClientModel,
            updates: UpdataClientSchema
        ) -> ClientModel:
    update_data = updates.model_dump()
    for key, value in update_data.items():
        setattr(client, key, value)
    session.commit()
    return client


async def delete_client(
            session: Session, client: ClientModel
        ) -> ClientModel:
    session.delete(client)
    session.commit()
    return client
