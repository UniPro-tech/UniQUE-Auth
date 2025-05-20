import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from database import engine, Base
from routers import router

# Create the database tables
Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
)

app.include_router(router)
