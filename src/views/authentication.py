from pydantic import BaseModel


from models import authentication as auth_model
from services import authentication as auth_service


class UserRequest(BaseModel):
    email: str
    password: str

    def to_model(self, tenant_id: int, oauth_provider: str) -> auth_model.User:
        return auth_service.new_user(
            tenant_id=tenant_id,
            email=self.email,
            password=self.password,
            oauth_provider=oauth_provider,
        )


class Token(BaseModel):
    email: str
