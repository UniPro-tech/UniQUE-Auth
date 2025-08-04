from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from dotenv import load_dotenv

from db import engine, Base, get_db
from unique_api.app.router.authorization import router as authorization_router
from unique_api.app.router.authentication import router as authentication_router


# .envファイルを読み込む
load_dotenv()

# データベースをリセット
# Base.metadata.drop_all(bind=engine)
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


if __name__ == "__main__":
    uvicorn.run("unique_api.app.main:app", reload=True, host="0.0.0.0")
