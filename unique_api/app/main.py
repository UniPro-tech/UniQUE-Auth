from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from dotenv import load_dotenv
import os
from unique_api.app.db import engine, Base, get_db
from unique_api.app.router.authorization import router as authorization_router
from unique_api.app.router.authentication import router as authentication_router
from unique_api.app.router.metadata import router as metadata_router


load_dotenv(".env")

# テスト環境では既存テーブルを削除してスキーマ不整合を防ぐ
env = os.getenv("ENV", "").lower()
reset_flag = os.getenv("RESET_DB", "").lower()
if env == "test" or reset_flag in ("1", "true", "yes"):
    Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)


# 立ち上がったらテスト用のデータを作成する
@asynccontextmanager
async def lifespan(app: FastAPI):
    from unique_api.app.data import create_test_data

    db = next(get_db())
    create_test_data(db)
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
)

app.include_router(authorization_router, tags=["Authorization"])
app.include_router(authentication_router, tags=["Authentication"])
app.include_router(metadata_router, tags=["Metadata"])


if __name__ == "__main__":
    uvicorn.run("unique_api.app.main:app", reload=True, host="0.0.0.0")
