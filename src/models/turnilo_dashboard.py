from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint


class TurniloDashboard(SQLModel, table=True):
    __tablename__ = "turniloDashboards"  # type: ignore
    __table_args__ = (UniqueConstraint('dataCube', 'shortName', name='_dataCube_shortName'),)

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    dataCube: str
    shortName: str = Field(index=True)
    name: str
    description: Optional[str] = ""
    hash: str
    preset: Optional[bool] = False
