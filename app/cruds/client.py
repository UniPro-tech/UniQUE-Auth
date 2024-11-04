from sqlalchemy import select
from sqlalchemy.orm import Session
from app.schemas import (
    UpdataClient as UpdataClientSchema,
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
        session.scalar(
            select(ClientModel)
            .where(ClientModel.id == client_id)
        )
    )
    return client if client else None


async def create_client(
            session: Session, user: UserModel,
            app: AppModel, user_client=True
        ) -> ClientModel:
    client = ClientModel()
    if user_client:
        client.user = user
    else:
        client.app = app
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
