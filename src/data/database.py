from typing import Any, Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy_utils import database_exists, create_database
import constants


def create_tables(db_engine) -> None:
    from models.turnilo_dashboard import TurniloDashboard
    SQLModel.metadata.create_all(db_engine, tables=[TurniloDashboard.__table__])


if constants.DRIVER == "sqlite":
    engine = create_engine("sqlite:///" + constants.SQLITE_FILE, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        "postgresql://"
        + constants.POSTGRES_USERNAME
        + ":"
        + constants.POSTGRES_PASSWORD
        + "@"
        + constants.POSTGRES_HOST
        + ":"
        + str(constants.POSTGRES_PORT)
        + "/"
        + constants.POSTGRES_DB)

if not database_exists(engine.url):
    print("Creating DB...")
    create_database(engine.url)  # type: ignore
    create_tables(engine)


def get_session() -> Generator[Session, Any, None]:
    db_session = Session(engine)
    try:
        yield db_session
    finally:
        db_session.close()
