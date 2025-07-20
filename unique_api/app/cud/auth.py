from sqlalchemy.orm import Session
from unique_api.app.model import (
    Auths,
)


def get_existing_auth(db: Session, user_id: int, app_id: str) -> Auths | None:
    return db.query(Auths).filter_by(auth_user_id=user_id, app_id=app_id).first()
