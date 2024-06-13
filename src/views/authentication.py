from pydantic import BaseModel
from passlib.context import CryptContext

from models.authentication import User as UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


class UserRequest(BaseModel):
    email: str
    password: str

    def to_model(self, tenant_id: int, oauth_provider: str) -> UserModel:
        return UserModel(
            tenant_id=tenant_id, 
            email=self.email, 
            hashed_password=get_password_hash(self.password), # TODO: Interline gibberish for extra protection
            oauth_provider=oauth_provider,
        )


