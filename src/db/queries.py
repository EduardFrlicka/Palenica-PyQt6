from sqlalchemy.orm import Session
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
