from sqlalchemy import Column, Integer, String, Boolean

from data.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True)  # Not sure about this one
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    oauth_provider = Column(String, default=None)  # Provider used to Register/Login this one

    def get_hashed_password(self) -> str:
        return self.hashed_password.to_string()
