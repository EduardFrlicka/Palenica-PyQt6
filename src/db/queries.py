from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import case
from datetime import date
import db


def get_all_seasons(session: Session = None):
    if session is None:
        with db.get_session() as session:
            seasons = get_all_seasons(session)
            session.expunge_all()
            return seasons

    seasons = session.query(db.Season).all()
    return seasons

def get_active_season(inside_date: date = date.today(), exclude_id: int = None, session: Session = None):
    if session is None:
        with db.get_session() as session:
            if session is None:
                raise Exception("Database connection error")
            
            return get_active_season(inside_date, session=session)

    season = session.query(db.Season).filter(db.Season.date_start <= inside_date, db.Season.date_end >= inside_date).filter(db.Season.id != exclude_id).first()
    return season


def get_season(season: int | db.Season, session: Session = None):
    if session is not None:
        if isinstance(season, int):
            return session.query(db.Season).get(season)
        if isinstance(season, db.Season):
            return session.query(db.Season).get(season.id)


def get_customer(customer: int | db.Customer, session: Session = None):
    if session is not None:
        if isinstance(customer, int):
            return session.query(db.Customer).get(customer)
        if isinstance(customer, db.Customer):
            return session.query(db.Customer).get(customer.id)


def get_production_line(line: int | str | db.Customer, session: Session = None):
    if session is not None:
        if isinstance(line, int):
            return session.query(db.ProductionLine).get(line)
        if isinstance(line, db.ProductionLine):
            return session.query(db.ProductionLine).get(line.id)
        if isinstance(line, str):
            return session.query(db.ProductionLine).filter_by(name=line).first()

    with db.get_session() as session:
        return get_production_line(line, session)

def get_production_lines(session: Session = None):
    if session is not None:
        return session.query(db.ProductionLine).all()

    with db.get_session() as session:
        res = get_production_lines(session)
        session.expunge_all()
        return res

def get_customer_la(customer: int | db.Customer, session: Session = None, season: int | db.Season = None):
    if session is None:
        with db.get_session() as session:
            return get_customer_la(customer, session)
    
    if season is None:
        season = get_active_season(session=session)
    
    if season is None:
        return 0.0

    customer_id = customer if isinstance(customer, int) else customer.id
    la = [
        session.query(
            func.sum(
                case(
                    (db.Season.id == season.id, db.Distilling.alcohol_volume_la),
                    else_=0.0,
                )
            ),
            db.Customer,
        )
        .outerjoin(db.Order, db.Customer.id == db.Order.customer_id)
        .outerjoin(db.Distilling, db.Distilling.order_id == db.Order.id)
        .outerjoin(db.Season, db.Season.id == db.Order.season_id)
        .group_by(db.Customer)
        .where(db.Customer.id == customer_id)
        .first()
    ]
    return la[0][0] if la else 0.0
