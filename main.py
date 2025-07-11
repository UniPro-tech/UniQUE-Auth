from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from db import engine, Base, get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from router import router
from data import create_test_data

Base.metadata.create_all(bind=engine)


# 立ち上がったらテスト用のデータを作成する
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    create_test_data(db)
    yield
    db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
)

app.include_router(router)


#http://localhost:8000/login?response_type=code&scope=openid+profile+email&client_id=test_client_id_091ba65c-a91b-4717-b44d-bb4882b21e1f&state=af0ifjsldkj&redirect_uri=https://example.com/callback
