from fastapi import FastAPI
from .routers import apps, flugs, users, tokens
from .database import engine, Base


# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(apps.router)
app.include_router(flugs.router)
app.include_router(users.router)
app.include_router(tokens.router)
