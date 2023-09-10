from .base import Base, STRING_LEN
from sqlalchemy import ForeignKey, Integer, String, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Any, List
from datetime import date
import db


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    mark: Mapped[str] = mapped_column(String(STRING_LEN), unique=True)

    production_date: Mapped[date] = mapped_column(Date)
    service_cost: Mapped[float] = mapped_column(Float)
    tax_vat: Mapped[float] = mapped_column(Float)
    tax_base: Mapped[float] = mapped_column(Float)
    cost_sum: Mapped[float] = mapped_column(Float)
    operating_costs: Mapped[float] = mapped_column(Float)

    distillings: Mapped[List["db.Distilling"]] = relationship()

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer: Mapped["db.Customer"] = relationship()

    season_id: Mapped[int] = mapped_column(ForeignKey("season.id"))
    season: Mapped["db.Season"] = relationship()

    production_line_id: Mapped[int] = mapped_column(ForeignKey("production_line.id"))
    production_line: Mapped["db.ProductionLine"] = relationship()

    def __init__(self, mark: str, production_date: date, service_cost: float, tax_vat: float, tax_base: float, cost_sum: float, operating_costs: float, distillings: "db.Distilling", customer: "db.Customer", season: "db.Season", production_line: "db.ProductionLine"):
        self.mark = mark
        self.service_cost = service_cost
        self.tax_vat = tax_vat
        self.tax_base = tax_base
        self.cost_sum = cost_sum
        self.operating_costs = operating_costs
        self.production_date = production_date
        self.distillings = distillings
        self.customer = customer
        self.season = season
        self.production_line = production_line
