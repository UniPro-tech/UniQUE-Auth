from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from app import routers
from app.database import engine, Base


# Create the database tables
Base.metadata.create_all(bind=engine)


middleware = [
    Middleware(SessionMiddleware, secret_key="your-secret-key")
]

app = FastAPI(
    root_path="/api/v1"
)

app.include_router(routers)
