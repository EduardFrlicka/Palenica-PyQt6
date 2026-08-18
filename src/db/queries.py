from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import case
from datetime import date
import db


def _run(session: Session, work):
    """Execute ``work(session)``.

    With a caller-supplied session the returned objects stay attached to it and
    the caller controls the transaction. Without one, a session is opened for
    the call and its results are detached before it closes, so they remain
    usable afterwards. Centralising this removes the copy-pasted
    "if session is None: open, recurse, expunge" dance every query used to carry
    - and with it the bug where get_season/get_customer simply returned None
    when no session was passed.
    """
    if session is not None:
        return work(session)

    with db.get_session() as owned:
        result = work(owned)
        owned.expunge_all()
        return result


def get_all_seasons(session: Session = None):
    return _run(session, lambda s: s.query(db.Season).all())


def get_active_season(inside_date: date = date.today(), exclude_id: int = None, session: Session = None):
    def work(s: Session):
        return (
            s.query(db.Season)
            .filter(db.Season.date_start <= inside_date, db.Season.date_end >= inside_date)
            .filter(db.Season.id != exclude_id)
            .first()
        )

    return _run(session, work)


def get_season(season: int | db.Season, session: Session = None):
    ident = season.id if isinstance(season, db.Season) else season
    return _run(session, lambda s: s.get(db.Season, ident))


def get_customer(customer: int | db.Customer, session: Session = None):
    ident = customer.id if isinstance(customer, db.Customer) else customer
    return _run(session, lambda s: s.get(db.Customer, ident))


def get_production_line(line: int | str | db.ProductionLine, session: Session = None):
    def work(s: Session):
        if isinstance(line, db.ProductionLine):
            return s.get(db.ProductionLine, line.id)
        if isinstance(line, int):
            return s.get(db.ProductionLine, line)
        return s.query(db.ProductionLine).filter_by(name=line).first()

    return _run(session, work)


def get_production_lines(session: Session = None):
    return _run(session, lambda s: s.query(db.ProductionLine).all())


def get_customer_la(customer: int | db.Customer, session: Session = None, season: int | db.Season = None):
    def work(s: Session):
        active = season if season is not None else get_active_season(session=s)
        if active is None:
            return 0.0

        customer_id = customer if isinstance(customer, int) else customer.id
        row = (
            s.query(
                func.sum(
                    case(
                        (db.Season.id == active.id, db.Distilling.alcohol_volume_la),
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
        )
        return row[0] if row else 0.0

    return _run(session, work)


def get_orders_overview(session: Session = None):
    """Flat rows backing the orders table.

    One tuple per order, with the columns in the exact order the table view and
    its sort/filter proxy address by index:
    (id, season_id, mark, production_line, production_date, name, address,
    birthday, la). Returning plain values rather than ORM objects keeps the
    query - and its session - out of the Qt model.
    """

    def work(s: Session):
        rows = (
            s.query(
                db.Order,
                db.Customer,
                db.Season,
                db.ProductionLine,
                func.sum(db.Distilling.alcohol_volume_la),
            )
            .outerjoin(db.Customer)
            .outerjoin(db.Season)
            .outerjoin(db.ProductionLine)
            .outerjoin(db.Distilling)
            .group_by(db.Order, db.Customer, db.Season, db.ProductionLine)
        )
        return [
            (
                order.id,
                season.id,
                order.mark,
                production_line.name,
                order.production_date,
                customer.name,
                customer.address,
                customer.birthday,
                la,
            )
            for order, customer, season, production_line, la in rows
        ]

    return _run(session, work)


def get_customers_overview(season_id: int = None, session: Session = None):
    """Flat rows backing the customers table.

    One tuple per customer: (id, name, address, birthday, la, phone). `la` is
    summed over every season, or only over `season_id` when one is given
    (None or -1 means "all seasons").
    """

    def work(s: Session):
        if season_id is None or season_id == -1:
            la_sum = func.sum(db.Distilling.alcohol_volume_la)
            rows = (
                s.query(db.Customer, la_sum)
                .outerjoin(db.Order, db.Customer.id == db.Order.customer_id)
                .outerjoin(db.Distilling, db.Distilling.order_id == db.Order.id)
                .group_by(db.Customer)
            )
        else:
            la_sum = func.sum(
                case(
                    (db.Season.id == season_id, db.Distilling.alcohol_volume_la),
                    else_=0.0,
                )
            )
            rows = (
                s.query(db.Customer, la_sum)
                .outerjoin(db.Order, db.Customer.id == db.Order.customer_id)
                .outerjoin(db.Distilling, db.Distilling.order_id == db.Order.id)
                .outerjoin(db.Season, db.Season.id == db.Order.season_id)
                .group_by(db.Customer)
            )
        return [
            (
                customer.id,
                customer.name,
                customer.address,
                customer.birthday,
                la,
                customer.phone_number,
            )
            for customer, la in rows
        ]

    return _run(session, work)
