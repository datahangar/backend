"""
Authentication service definition for the DataHangar backend.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.exceptions import http as http_exceptions
from src import constants
from src.views import authentication as auth_view
from src.models import authentication as auth_model
import constants


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def new_user(tenant_id: int, email: str, password: str, oauth_provider: str) -> auth_model.User:
    return auth_model.User(
        tenant_id=tenant_id,
        email=email,
        hashed_password=get_password_hash(password),
        oauth_provider=oauth_provider
    )


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM)
    return encoded_jwt


def parse_token(token: str) -> auth_view.Token:
    try:
        payload = jwt.decode(token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
        return auth_view.Token(**payload)
    except JWTError:
        raise http_exceptions.new_credentials_exception()


async def get_current_user(token: str, db: Session):
    t = parse_token(token)
    user = get_user_by_email(db, email=t.email)
    if user is None:
        raise http_exceptions.new_credentials_exception()
    return user


async def get_user_by_email(db: Session, email: str) -> auth_model.User:
    return db.query(auth_model.User).filter(auth_model.User.email == email).one()


async def create_user(db: Session, user: auth_model.User) -> auth_model.User:
    # TODO: Maybe we could create the transaction for the session before calling this function?
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
