import os
from sqlalchemy import create_engine, text

def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url

def make_engine():
    return create_engine(get_database_url(), pool_pre_ping=True)

def db_ping(engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("select 1"))
