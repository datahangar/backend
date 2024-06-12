import re
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from models.turnilo_dashboard import TurniloDashboard
from services import turnilo_dashboards as td

import constants
import data.database as db

turnilo_router = APIRouter()

### Dashboards ###


def is_valid_query(s: str) -> bool:
    if not isinstance(s, str):
        return False
    if len(s) > 256:
        return False
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, s))


@turnilo_router.get(
    constants.URL_PATH + "/turnilo/dashboards/",
    response_model=List[TurniloDashboard],
    summary="Gets all Turnilo dashboards"
)
def turnilo_get_dashboards(db_session: Session = Depends(db.get_session),
                           shortName: str = Query(None), dataCube: str = Query(None)):
    if shortName and not is_valid_query(shortName):
        raise HTTPException(status_code=400, detail=f"Invalid shortName='{shortName}'")
    if dataCube and not is_valid_query(dataCube):
        raise HTTPException(status_code=400, detail=f"Invalid dataCube='{dataCube}'")
    return td.dashboards_get_all(db_session, shortName, dataCube)


@turnilo_router.get(
    constants.URL_PATH + "/turnilo/dashboards/{id}",
    response_model=TurniloDashboard,
    summary="Get a Turnilo dashboard by id (integer)"
)
def turnilo_get_dashboard_id(id: str, db_session: Session = Depends(db.get_session)):
    try:
        int_id = int(id)
    except BaseException:
        raise HTTPException(status_code=400, detail="Id is not an integer")
    return td.dashboards_get_id(db_session, int_id)


@turnilo_router.post(
    constants.URL_PATH + "/turnilo/dashboards/",
    response_model=TurniloDashboard,
    summary="Create a Turnilo dashboard. A unique id will be assigned."
)
def turnilo_create_dashboard(dashboard: TurniloDashboard, db_session: Session = Depends(db.get_session)):
    return td.dashboards_create(db_session, dashboard)


@turnilo_router.put(
    constants.URL_PATH + "/turnilo/dashboards/{id}",
    response_model=TurniloDashboard,
    summary="Update/replace a Turnilo dashboard. The dashboard (id) must exist"
)
def turnilo_update_dashboard(id: str, dashboard: TurniloDashboard, db_session: Session = Depends(db.get_session)):
    try:
        int_id = int(id)
        dashboard.id = int_id
    except BaseException:
        raise HTTPException(status_code=400, detail="Id is not an integer")
    return td.dashboards_update(db_session, dashboard)


@turnilo_router.delete(
    constants.URL_PATH + "/turnilo/dashboards/{id}",
    response_model=TurniloDashboard,
    summary="Delete a Turnilo dashboard"
)
def turnilo_delete_dashboard(id: str, db_session: Session = Depends(db.get_session)):
    try:
        int_id = int(id)
    except BaseException:
        raise HTTPException(status_code=400, detail="Id is not an integer")
    return td.dashboards_delete(db_session, int_id)
