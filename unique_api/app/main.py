from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from db import engine, Base, get_db
from unique_api.app.router import router
from data import create_test_data

# データベースをリセット
# Base.metadata.drop_all(bind=engine)
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

if __name__ == "__main__":
    uvicorn.run("unique_api.app.main:app", reload=True, host="0.0.0.0")
