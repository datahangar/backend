import http
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config as StarletteConfig
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from data import database as db
from exceptions import http as http_exceptions
from src.views import authentication as auth_view
from src.models import authentication as auth_model
from src.services import authentication as auth_service

auth_router = APIRouter()


SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


config = StarletteConfig()
oauth = OAuth(config)


@auth_router.post("/register")
async def register_user(user: auth_view.UserRequest, db: Session = Depends(db.get_session)):
    db_user = auth_service.get_user_by_email(db, user.email)
    if db_user:
        raise http_exceptions.new_conflict_exception("User already exists")
    await auth_service.create_user(db, user.to_model(tenant_id=1, oauth_provider="local"))
    # TODO: Find response model
    return {"message": "User registered successfully"}


@auth_router.post("/token", response_model=auth_view.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(db.get_session)):
    user = await auth_service.get_user_by_email(db, form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.get_hashed_password()):
        raise http_exceptions.new_user_not_found_exception()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/protected")
async def read_protected_route(current_user: auth_model.User = Depends(auth_service.get_current_user)):
    return {"message": "You are authenticated!", "user": current_user.email}
