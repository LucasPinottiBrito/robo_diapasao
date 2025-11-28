import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

db_path = os.environ.get("ROBO_DB_PATH", "database.db")

engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"check_same_thread": False},
    echo=False,
    future=True,
)

@event.listens_for(engine, "connect")
def _set_sqlite_pragma(conn, _):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)

def get_session() -> Session:
    return SessionLocal()
