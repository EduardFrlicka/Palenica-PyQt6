import db
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session
from datetime import date, datetime
import config
from dialogs.alert import error, alert
from messages import DATABASE_CONFIG_ERROR, DATABASE_OFFLINE


def engine_init():

    database_config: dict = config.config.get("database")
    if not database_config:
        error(DATABASE_CONFIG_ERROR)
        return None

    try:
        db_url = URL.create(
            database_config.get("engine"),
            database_config.get("user"),
            database_config.get("password"),
            database_config.get("host"),
            database_config.get("port"),
            database_config.get("path"),
        )
        engine = create_engine(db_url)

    except Exception as e:
        alert(DATABASE_OFFLINE)
        return None

    return engine


engine = engine_init()


def create_all(engine=engine):
    db.Base.metadata.create_all(engine)


def drop_all(engine=engine):
    db.Base.metadata.drop_all(engine)


def populate(engine=engine):
    session = Session(engine)

    season = db.Season(date(year=2024, month=8, day=1), date(year=2025, month=8, day=1))

    line_a = db.ProductionLine("A")
    session.add(line_a)
    session.add(db.ProductionLine("B"))

    session.add(season)
    # for i in range(500):
    #     customer = (db.Customer(f"Martin{i}", f"Kukucinova {(500-i)//10}",
    #                             date(year=2000+i//300, month=(i//28) % 12 + 1, day=i % 28+1), "09045555555"))
    #     session.add(customer)
    #     for j in range(10):
    #         distillings = [db.Distilling(
    #             15, 15, 15, 15, 15, 15, 15, 15, 15, 15) for _ in range(2)]
    #         map(session.add, distillings)
    #         session.add(db.Order(f"{i}/{j}", date.today(), 0.0, 0.0,
    #                     0.0, 0.0, 0.0, distillings, customer, season, line_a))

    session.commit()
    session.refresh(season)
    season.activate(session)
    session.commit()
    session.close()
