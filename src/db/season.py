from typing import Any
import db
from datetime import date
from sqlalchemy import ForeignKey, Integer, String, Float, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session


class Season(db.Base):
    __tablename__ = "season"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    active: Mapped[bool] = mapped_column(
        Boolean, default=None, nullable=True, unique=True)
    date_start: Mapped[date] = mapped_column(Date)
    date_end: Mapped[date] = mapped_column(Date)

    def __init__(self, date_start: date, date_end: date):
        self.date_start = date_start
        self.date_end = date_end
        

    def activate(self, session: Session):
        for season in session.query(Season).all():
            season.active = None
            session.add(season)

        self.active = True
        session.add(self)
        session.commit()
