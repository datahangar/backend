import re
from typing import List, Optional
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from sqlalchemy import exc
from models.turnilo_dashboard import TurniloDashboard
from fastapi import HTTPException

# Turnilo Dashboards


class GetQueryParams(BaseModel):
    """
    Get query filtering params
    """
    shortName: Optional[str] = Field(default=None, description="Dashboard's shortName")
    dataCube: Optional[str] = Field(default=None, description="Dashboard's dataCube")

    def is_valid_param(self, s: str) -> bool:
        if len(s) > 256:
            return False
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, s))

    def validate(self):
        if self.shortName and not self.is_valid_param(self.shortName):
            raise HTTPException(status_code=400, detail=f"Invalid shortName='{self.shortName}'")
        if self.dataCube and not self.is_valid_param(self.dataCube):
            raise HTTPException(status_code=400, detail=f"Invalid dataCube='{self.dataCube}'")


def dashboards_get_all(session: Session, query_params: GetQueryParams) -> List[TurniloDashboard]:
    statement = select(TurniloDashboard)
    if query_params.shortName:
        statement = statement.where(TurniloDashboard.shortName == query_params.shortName)
    if query_params.dataCube:
        statement = statement.where(TurniloDashboard.dataCube == query_params.dataCube)
    return list(session.exec(statement).all())


def _dashboards_return_single_obj(results: List[TurniloDashboard]):
    if results is None or len(results) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    elif len(results) > 1:
        raise HTTPException(status_code=500, detail="Corrupted state. Get query returned > 1 result")
    return results[0]


def dashboards_get_id(session: Session, _id: int) -> TurniloDashboard:
    statement = select(TurniloDashboard).where(TurniloDashboard.id == _id)
    results: List[TurniloDashboard] = list(session.exec(statement).all())
    return _dashboards_return_single_obj(results)


def dashboards_create(session: Session, dashboard: TurniloDashboard) -> TurniloDashboard:
    if dashboard.id:
        raise HTTPException(status_code=400, detail="'id' must NOT be set")
    if not dashboard.shortName or dashboard.shortName == "":
        raise HTTPException(status_code=400, detail="shortName not present or empty")
    try:
        session.add(dashboard)
        session.commit()
    except exc.IntegrityError as e:
        print(str(e))
        raise HTTPException(status_code=400, detail="Integrity error: duplicated datacube+shortName")
    print("Created dashboard: " + str(dashboard.id))
    print(dashboard)
    return dashboard


def dashboards_update(session: Session, dashboard: TurniloDashboard) -> TurniloDashboard:
    if not dashboard.id:
        raise HTTPException(status_code=400, detail="'id' MUST be set")
    if not dashboard.shortName or dashboard.shortName == "":
        raise HTTPException(status_code=400, detail="shortName not present or empty")

    # First check if it exists
    dashboards_get_id(session, dashboard.id)
    try:
        session.merge(dashboard)
        session.commit()
    except exc.IntegrityError as e:
        print(str(e))
        raise HTTPException(status_code=400, detail="Integrity error: duplicated datacube+shortName")
    print("Updated dashboard:" + str(dashboard.id))
    print(dashboard)
    return dashboard


def dashboards_delete(session: Session, _id: int) -> TurniloDashboard:
    dashboard = None
    try:
        statement = select(TurniloDashboard).where(TurniloDashboard.id == _id)
        dashboard = session.exec(statement).one()
    except BaseException:
        pass
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(dashboard)
    session.commit()
    print("Deleted dashboard:")
    print(dashboard)
    return dashboard
