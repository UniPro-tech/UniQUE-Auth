from sqlalchemy.orm import Session
from ..schemas import (
    UserLog as UserLogSchema,
    AppLog as AppLogSchema,
    FlagLog as FlagLogSchema,
    RoleLog as RoleLogSchema,
)
from ..models import (
    UserLog,
    AppLog,
    FlagLog,
    RoleLog,
)


async def get_user_logs(db: Session, user_id: int, limit: int, offset: int):
    logs = (db.query(UserLog)
            .filter(UserLog.user_id == user_id)
            .limit(limit).offset(offset).all()
            )
    return [UserLogSchema.model_validate(log) for log in logs]


async def get_app_logs(db: Session, app_id: int, limit: int, offset: int):
    logs = (db.query(AppLog)
            .filter(AppLog.app_id == app_id)
            .limit(limit).offset(offset).all()
            )
    return [AppLogSchema.model_validate(log) for log in logs]


async def get_flag_logs(db: Session, flag_id: int, limit: int, offset: int):
    logs = (db.query(FlagLog)
            .filter(FlagLog.flag_id == flag_id)
            .limit(limit).offset(offset).all()
            )
    return [FlagLogSchema.model_validate(log) for log in logs]


async def get_role_logs(db: Session, role_id: int, limit: int, offset: int):
    logs = (db.query(RoleLog)
            .filter(RoleLog.role_id == role_id)
            .limit(limit).offset(offset).all()
            )
    return [RoleLogSchema.model_validate(log) for log in logs]


async def create_user_log(db: Session, log: UserLogSchema):
    log = UserLog(**log.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return UserLogSchema.model_validate(log)


async def create_app_log(db: Session, log: AppLogSchema):
    log = AppLog(**log.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return AppLogSchema.model_validate(log)


async def create_flag_log(db: Session, log: FlagLogSchema):
    log = FlagLog(**log.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return FlagLogSchema.model_validate(log)


async def create_role_log(db: Session, log: RoleLogSchema):
    log = RoleLog(**log.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return RoleLogSchema.model_validate(log)


async def delete_user_log(db: Session, log_id: int):
    log = db.query(UserLog).filter(UserLog.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
        return UserLogSchema.model_validate(log)
    return None


async def delete_app_log(db: Session, log_id: int):
    log = db.query(AppLog).filter(AppLog.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
        return AppLogSchema.model_validate(log)
    return None


async def delete_flag_log(db: Session, log_id: int):
    log = db.query(FlagLog).filter(FlagLog.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
        return FlagLogSchema.model_validate(log)
    return None


async def delete_role_log(db: Session, log_id: int):
    log = db.query(RoleLog).filter(RoleLog.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
        return RoleLogSchema.model_validate(log)
    return None
