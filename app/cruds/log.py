from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Log


async def get_user_logs(
            session: Session, user_id: int,
            limit: int, offset: int
        ):
    logs = (
        session.scalar(
            select(Log)
            .where(Log.user_id == user_id)
            .limit(limit).offset(offset)
        )
    )
    return logs


async def get_app_logs(session: Session, app_id: int, limit: int, offset: int):
    logs = (
        session.scalar(
            select(Log)
            .where(Log.app_id == app_id)
            .limit(limit).offset(offset)
        )
    )
    return logs
