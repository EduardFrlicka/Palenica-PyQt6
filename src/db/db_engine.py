from sqlalchemy import Engine
import db
from sqlalchemy.orm import Session
from datetime import date, datetime
import config

engine: Engine = None


def engine_init():
    from sqlalchemy import create_engine, URL

    db_url = URL.create(
        config.config["database"].get("engine"),
        config.config["database"].get("user"),
        config.config["database"].get("password"),
        config.config["database"].get("host"),
        config.config["database"].get("port"),
        config.config["database"].get("path"),
    )

    # db_url = URL.create("sqlite", None, None, None, None, "palenica.db")
    return create_engine(db_url)


def __getattr__(name: str):
    if name == "engine":
        global engine
        if not engine:
            engine = engine_init()
        return engine

    raise AttributeError(f"Module {__name__!r} has no attribute {name!r}")


def create_all(engine=__getattr__("engine")):
    db.Base.metadata.create_all(engine)


def drop_all(engine=engine):
    db.Base.metadata.drop_all(engine)


def populate(engine=engine):
    session = Session(engine)

    season = db.Season(
        date(year=2024, month=8, day=1), date(year=2025, month=8, day=1)
    )

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
