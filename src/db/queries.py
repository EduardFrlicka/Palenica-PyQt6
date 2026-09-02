from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import and_, case, or_
from datetime import date
import calculations
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


def get_order(order: int | db.Order, session: Session = None):
    if session is not None:
        ident = order.id if isinstance(order, db.Order) else order
        return session.get(db.Order, ident)

    with db.get_session() as session:
        res = get_order(order, session)
        session.expunge_all()
        return res


def get_customer_la_before(
    customer: int | db.Customer,
    order: db.Order = None,
    season: int | db.Season = None,
    session: Session = None,
):
    """LA the customer has accumulated in `season` ahead of `order`.

    This is what the excise tiering is measured against. Without `order` it is
    the customer's whole season total - what a brand new order sees. With one,
    only the orders that precede it count, ordered by production date and by id
    within a day: re-saving an existing order must not stack its own litres on
    top of itself, or every edit would push the order a tier higher.
    """
    if session is None:
        with db.get_session() as session:
            return get_customer_la_before(customer, order, season, session)

    if season is None:
        season = order.season if order is not None else get_active_season(session=session)

    if season is None:
        return 0.0

    customer_id = customer if isinstance(customer, int) else customer.id
    season_id = season if isinstance(season, int) else season.id

    query = (
        session.query(func.coalesce(func.sum(db.Distilling.alcohol_volume_la), 0.0))
        .join(db.Order, db.Distilling.order_id == db.Order.id)
        .filter(db.Order.customer_id == customer_id)
        .filter(db.Order.season_id == season_id)
    )

    if order is not None:
        query = query.filter(
            or_(
                db.Order.production_date < order.production_date,
                and_(
                    db.Order.production_date == order.production_date,
                    db.Order.id < order.id,
                ),
            )
        )

    return query.scalar() or 0.0


def get_orders_after(order: db.Order, session: Session = None):
    """The same customer's later orders in the same season, in accumulation order.

    Returned as `calculations.OrderTaxInput` rows rather than ORM objects, so
    the recalculation check that consumes them stays a pure function. `order`
    itself is excluded - it is the one being edited or deleted.
    """
    if session is None:
        with db.get_session() as session:
            return get_orders_after(order, session)

    later_orders = (
        session.query(db.Order)
        .filter(db.Order.customer_id == order.customer_id)
        .filter(db.Order.season_id == order.season_id)
        .filter(
            or_(
                db.Order.production_date > order.production_date,
                and_(
                    db.Order.production_date == order.production_date,
                    db.Order.id > order.id,
                ),
            )
        )
        .order_by(db.Order.production_date, db.Order.id)
        .all()
    )

    return [
        calculations.OrderTaxInput(
            later.id,
            later.mark,
            later.production_date,
            sum(distilling.sum_tax for distilling in later.distillings),
            tuple(distilling.alcohol_volume_la for distilling in later.distillings),
            later.constants.lower_tax,
            later.constants.full_tax,
            later.constants.lower_tax_la_limit,
        )
        for later in later_orders
    ]


def delete_order(order: int | db.Order, session: Session = None):
    """Delete an order. Its distillings go with it, through the relationship."""
    if session is None:
        with db.get_session() as session:
            delete_order(order, session)
            return

    order = get_order(order, session)
    if order is None:
        return

    session.delete(order)
    session.commit()
