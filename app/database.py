import os
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
)
from dotenv import load_dotenv

# .envファイルの内容を読み込見込む
load_dotenv(dotenv_path='/home/sibainu/Project/UniQUE-API/.env')

SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']


class Base(DeclarativeBase):
    pass


engine = create_engine(
    SQLALCHEMY_DATABASE_URI, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DBマイグレーションを行う.
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
