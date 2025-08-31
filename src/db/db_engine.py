import traceback
import db
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session
from datetime import date, datetime
import config
from dialogs.alert import error, alert
from messages import DATABASE_CONFIG_ERROR, DATABASE_OFFLINE
import oracledb
from typing import Generator

def engine_init():
    database_config: dict = config.config.get("database")
    if not database_config:
        error(DATABASE_CONFIG_ERROR)
        return None

    try:
        # db_url = URL.create(
        #     database_config.get("engine"),
        #     database_config.get("user"),
        #     database_config.get("password"),
        #     database_config.get("host"),
        #     database_config.get("port"),
        #     database_config.get("path"),
        # )
        # engine = create_engine(
        #     "oracle+oracledb://@",
        #         # thick_mode={
        #         #     # directory containing tnsnames.ora and cwallet.so
        #         #     "config_dir": "./oracle",
        #         # },
        #     connect_args={
        #         "user": database_config.get("user"),
        #         "password": database_config.get("password"),
        #         "dsn": database_config.get("dsc"),
        #     },
        # )

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

        print("Connected to Oracle database successfully.")

        # db.Base.metadata.drop_all(engine)
        # db.Base.metadata.create_all(engine)

        # with Session(engine) as session:
        #     season = session.query(db.Season).first()  # Test connection and metadata
        #     if not season:
        #         session.add(db.Season(date_start=date.today(), date_end=date.today()))
        #         session.add(db.ProductionLine("A"))
        #         session.add(db.ProductionLine("B"))
        #         session.commit()
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