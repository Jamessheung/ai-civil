import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url


def get_database_url() -> str:
    """
    Read DATABASE_URL from environment.
    This must be set in Render -> Environment Variables.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def make_engine():
    """
    Create SQLAlchemy engine.
    Also print a sanitized DB URL (password hidden) for debugging in Render logs.
    """
    url = get_database_url()

    # Print a sanitized URL (password hidden) to confirm which host/user/port is being used.
    try:
        u = make_url(url)
        print("DB_URL_SANITIZED:", u.render_as_string(hide_password=True), flush=True)
    except Exception as e:
        # If parsing fails (e.g., malformed URL), still print a safe hint.
        print(f"DB_URL_SANITIZED: <unparseable DATABASE_URL> ({e})", flush=True)

    return create_engine(url, pool_pre_ping=True)


def db_ping(engine) -> None:
    """
    Minimal DB connectivity check.
    """
    with engine.connect() as conn:
        conn.execute(text("select 1"))

