from sqlalchemy.orm import Session
from ..schemas import (
    Client as ClientSchema,
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
            ) -> ClientSchema:
    client = (
        session.query(ClientModel)
        .filter(ClientModel.id == client_id)
        .first()
    )
    return ClientSchema.model_validate(client) if client else None


async def create_client(
        session: Session, client: ClientModel,
        user: UserSchema, app: AppSchema, user_client=True
        ) -> ClientSchema:
    if user_client:
        client.user = UserModel(**user.model_dump())
    else:
        client.app = AppModel(**app.model_dump())
    session.add(client)
    session.commit()
    session.refresh(client)
    return ClientSchema.model_validate(client)


async def update_user_client(
            session: Session,
            client: ClientModel,
            updates: UpdataClientSchema
        ) -> ClientSchema:
    update_data = updates.model_dump()
    for key, value in update_data.items():
        setattr(client, key, value)
    session.commit()
    return ClientSchema.model_validate(client)


async def delete_client(
            session: Session, client: ClientModel
        ) -> ClientSchema:
    session.delete(client)
    session.commit()
    return ClientSchema.model_validate(client)
