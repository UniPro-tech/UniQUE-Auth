from fastapi import Depends, FastAPI, HTTPException, Header, Body
from sqlalchemy.orm import Session
import app.crud as crud
import models
import schemas
from app.database import SessionLocal, engine, get_db
import logging
from typing import List


logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/session", response_model=schemas.User)
def login_user(user: str, db: Session = Depends(get_db)):
    #db_user = crud.get_user_by_email_password(
    #    db, email=email, password=password
    #    )
    #if db_user is None:
    #    raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User logged in"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/v1/token/code")
async def get_token_code(
        header: List[str] = Header(),
        body:str = Body()
    ):
    
    return {header:body}
