from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy_utils import database_exists, create_database
from constants import *

def createTables(db_engine):
    from models.turnilo_dashboard import TurniloDashboard
    SQLModel.metadata.create_all(db_engine)

if DRIVER == "sqlite":
    engine = create_engine("sqlite:///"+SQLITE_FILE, connect_args={"check_same_thread": False})
else:
    engine = create_engine("postgresql://"+POSTGRES_USERNAME+":"+POSTGRES_PASSWORD+"@"+POSTGRES_HOST+":"+str(POSTGRES_PORT)+"/"+POSTGRES_DB)

if not database_exists(engine.url):
    print("Creating DB...")
    create_database(engine.url)
    createTables(engine)

def get_session():
    db_session = Session(engine)
    try:
        yield db_session
    finally:
        db_session.close()
