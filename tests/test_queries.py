"""Tests for the db query layer: the unified session handling and the flat
"overview" rows the Qt table models consume.

These import the SQLAlchemy/libsql stack, so they are skipped where it is not
installed (notably the CI 'test' job, which installs only pytest+requests) and
run anywhere the app's runtime dependencies are present.
"""

from datetime import date, timedelta

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("libsql")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import db
from db import db_engine


@pytest.fixture
def seeded(monkeypatch):
    """An in-memory database with one fully-populated order, wired in as the
    engine db.get_session() hands out."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one shared in-memory db across sessions
    )
    db.Base.metadata.create_all(engine)
    monkeypatch.setattr(db_engine, "engine", engine)

    today = date.today()
    with Session(engine) as s:
        line_a = db.ProductionLine("A")
        line_b = db.ProductionLine("B")
        active = db.Season(today - timedelta(days=1), today + timedelta(days=1))
        past = db.Season(today - timedelta(days=40), today - timedelta(days=30))
        customer = db.Customer("Jan Novak", "Main St 1", date(1980, 5, 17), "0900123456")
        constants = db.CalculationConstants(7.452, 14.904, 43.0, 0.20, 8.2)
        distilling = db.Distilling(100.0, "hrusky", 20.0, 52.0, 18.0, 0.51, 10.0, 74.52, 0.0, 74.52)
        order = db.Order("1", today, 100.0, 0.0, 0.0, 0.0, 0.0, [distilling], customer, active, line_a, constants)
        s.add_all([line_a, line_b, active, past, customer, constants, distilling, order])
        s.commit()
        ids = {
            "customer": customer.id,
            "order": order.id,
            "active_season": active.id,
            "past_season": past.id,
        }
    return ids


# --- the fix: sessionless lookups now actually query -----------------------


def test_get_customer_without_session_returns_the_row(seeded):
    customer = db.get_customer(seeded["customer"])
    assert customer is not None  # used to silently return None
    assert customer.name == "Jan Novak"


def test_get_season_without_session_returns_the_row(seeded):
    season = db.get_season(seeded["active_season"])
    assert season is not None  # used to silently return None
    assert season.to_string()  # detached object is still usable


def test_get_customer_accepts_an_orm_object(seeded):
    customer = db.get_customer(seeded["customer"])
    again = db.get_customer(customer)
    assert again.id == customer.id


def test_get_all_seasons_and_lines_without_session(seeded):
    assert len(db.get_all_seasons()) == 2
    assert {line.name for line in db.get_production_lines()} == {"A", "B"}


# --- get_active_season honours exclude_id through the sessionless path ------


def test_get_active_season_finds_today(seeded):
    active = db.get_active_season()
    assert active is not None
    assert active.id == seeded["active_season"]


def test_get_active_season_exclude_id(seeded):
    # Excluding the only current season leaves nothing active.
    assert db.get_active_season(exclude_id=seeded["active_season"]) is None


# --- customer LA -----------------------------------------------------------


def test_get_customer_la_sums_active_season(seeded):
    assert db.get_customer_la(seeded["customer"]) == 10.0


# --- overview rows the Qt models consume -----------------------------------


def test_orders_overview_row_shape(seeded):
    rows = db.get_orders_overview()
    assert len(rows) == 1
    (order_id, season_id, mark, line, prod_date, name, address, birthday, la) = rows[0]
    assert order_id == seeded["order"]
    assert season_id == seeded["active_season"]
    assert (mark, line, name, address) == ("1", "A", "Jan Novak", "Main St 1")
    assert prod_date == date.today()
    assert birthday == date(1980, 5, 17)
    assert la == 10.0


def test_customers_overview_all_seasons(seeded):
    rows = db.get_customers_overview(None)
    assert len(rows) == 1
    cid, name, address, birthday, la, phone = rows[0]
    assert (cid, name, la, phone) == (seeded["customer"], "Jan Novak", 10.0, "0900123456")


def test_customers_overview_filters_by_season(seeded):
    # The order sits in the active season, so the past season sums to zero.
    (row,) = db.get_customers_overview(seeded["active_season"])
    assert row[4] == 10.0
    (row,) = db.get_customers_overview(seeded["past_season"])
    assert row[4] == 0.0
