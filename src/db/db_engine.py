import traceback
import db
from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import Session
from datetime import date, datetime
import config
from . import turso_dialect  # registers the sqlite+turso:// URL scheme
from .errors import DatabaseUnavailable, DatabaseConfigError, DatabaseOffline
from messages import DATABASE_CONFIG_ERROR, DATABASE_OFFLINE
from typing import Generator


def engine_init():
    """Create the SQLAlchemy engine, or raise a DatabaseUnavailable.

    Raising rather than reporting keeps this free of the GUI: the caller decides
    how to present the failure and whether it is fatal (see app.main).
    """
    database_config: dict = config.config.get("database")
    if not database_config:
        raise DatabaseConfigError(DATABASE_CONFIG_ERROR)

    url = database_config.get("url")
    if not url:
        raise DatabaseConfigError(DATABASE_CONFIG_ERROR)

    try:
        # Turso: sqlite+turso://<host>.turso.io/?authToken=<token>
        print("Connecting to database...")

        engine = create_engine(
            url,
            pool_pre_ping=True,  # hosted databases drop idle connections
        )

        with engine.connect() as connection:
            connection.execute(text("select 1"))

        print("Connected to database successfully.")
    except Exception as exc:
        traceback.print_stack()
        print(exc)
        raise DatabaseOffline(DATABASE_OFFLINE) from exc

    print("Database engine initialized successfully.")
    return engine


engine = None
_init_attempted = False
_init_error: DatabaseUnavailable | None = None


def get_engine():
    """Return the database engine, or None if it is unavailable.

    The connection is attempted once and the failure is remembered, so the
    repeated ``get_engine() is None`` checks callers use to fall back to
    manual/offline mode neither reconnect nor re-report. Inspect the cached
    failure with get_engine_error().
    """
    global engine, _init_attempted, _init_error
    if engine is None and not _init_attempted:
        _init_attempted = True
        try:
            engine = engine_init()
        except DatabaseUnavailable as exc:
            _init_error = exc
    return engine


def get_engine_error() -> "DatabaseUnavailable | None":
    """The failure from the connection attempt, or None if it never failed."""
    return _init_error


def get_session() -> Session:
    """
    Returns a new session for the database engine.
    """
    if engine is None:
        raise Exception("Database engine is not initialized.")

    return Session(engine)


def get_session_generator() -> Generator[Session, None, None]:
    """
    Returns a generator that yields a new session for the database engine.
    """
    if engine is None:
        raise Exception("Database engine is not initialized.")

    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
