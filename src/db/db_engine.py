import traceback
import db
from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import Session
from datetime import date, datetime
import config
from dialogs.alert import error, alert
from messages import DATABASE_CONFIG_ERROR, DATABASE_OFFLINE
from typing import Generator

def engine_init():
    database_config: dict = config.config.get("database")
    if not database_config:
        error(DATABASE_CONFIG_ERROR)
        return None

    try:
        url = database_config.get("url")

        if url:
            # SQLite Cloud: sqlitecloud://<host>:8860/<database>?apikey=<key>
            print("Connecting to database...")

            engine = create_engine(
                url,
                pool_pre_ping=True,  # hosted databases drop idle connections
            )

            with engine.connect() as connection:
                connection.execute(text("select 1"))
        else:
            print("Connecting to Oracle database...")

            connection = oracledb.connect(
                user=database_config.get("user"),
                password=database_config.get("password"),
                dsn=database_config.get("dsn"),
            )

            engine = create_engine(
                "oracle+oracledb://",
                creator=lambda: connection,
            )

        print("Connected to database successfully.")

        # db.Base.metadata.drop_all(engine)
        # db.Base.metadata.create_all(engine)

        # with Session(engine) as session:
        #     season = session.query(db.Season).first()  # Test connection and metadata
            # if not season:
            #     session.add(db.Season(date_start=date.today(), date_end=date.today()))

            # session.add(db.ProductionLine("A"))
            # session.add(db.ProductionLine("B"))
            # session.commit()
        print("Database engine initialized successfully.")

    except Exception as e:
        # traceback.print_exc()
        traceback.print_stack()
        print(e)
        alert(DATABASE_OFFLINE)
        return None

    return engine

engine = None
# engine = engine_init()

def get_engine():
    """
    Returns the database engine.
    """
    global engine
    if engine is None:
        engine = engine_init()
    return engine

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