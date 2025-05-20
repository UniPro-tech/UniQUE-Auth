import os
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
)
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# .envファイルの内容を読み込見込む
load_dotenv(dotenv_path='/home/sibainu/Project/UniQUE-API/.env')

#SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

print(SQLALCHEMY_DATABASE_URI)
Base = declarative_base()


engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
    echo=True
)
SessionLocal = sessionmaker(bind=engine)

# DBマイグレーションを行う.
# Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
