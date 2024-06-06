from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import exc
from models.turnilo_dashboard import TurniloDashboard
from fastapi import HTTPException

# Turnilo Dashboards


def dashboards_get_all(session: Session) -> List[TurniloDashboard]:
    return session.query(TurniloDashboard).all()


def _dashboards_return_single_obj(results: List[TurniloDashboard]):
    if results is None or len(results) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    elif len(results) > 1:
        raise HTTPException(status_code=500, detail="Corrupted state. Get query returned > 1 result")
    return results[0]


def dashboards_get_id(session: Session, _id: int) -> TurniloDashboard:
    results: List[TurniloDashboard] = session.query(TurniloDashboard).filter_by(id=_id).all()
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
        dashboard = session.query(TurniloDashboard).filter_by(id=_id).one()
    except BaseException:
        pass
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(dashboard)
    session.commit()
    print("Deleted dashboard:")
    print(dashboard)
    return dashboard
