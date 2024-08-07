from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import case
import db


def get_active_season(session: Session = None):
    if session is not None:
        return session.query(db.Season).filter(db.Season.active == True).first()
    with Session(db.engine) as session:
        return session.query(db.Season).filter(db.Season.active == True).first()


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


def get_customer_la(customer: int | db.Customer, session: Session = None):
    if session is None:
        with Session(db.engine) as session:
            return get_customer_la(customer, session)

    customer_id = customer if isinstance(customer, int) else customer.id
    la = [
        session.query(
            func.sum(
                case(
                    (db.Season.active, db.Distilling.alcohol_volume_la),
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
