from typing import Any, List
import db
from datetime import date
from sqlalchemy import ForeignKey, Integer, String, Float, Boolean, Date, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from constants import DATE_FORMAT


class Season(db.Base):
    __tablename__ = "season"
    id_seq = Sequence("season_id_seq", start=1, increment=1)
    id: Mapped[int] = mapped_column(Integer, id_seq, primary_key=True)

    date_start: Mapped[date] = mapped_column(Date)
    date_end: Mapped[date] = mapped_column(Date)

    def __init__(self, date_start: date, date_end: date):
        self.date_start = date_start
        self.date_end = date_end

    def to_string(self) -> str:
        if self.date_start is None or self.date_end is None:
            return "No season"
        
        return f"{self.date_start.strftime(DATE_FORMAT)} - {self.date_end.strftime(DATE_FORMAT)}"
    
    # def activate(self, session: Session):
    #     for season in session.query(Season).all():
    #         season.active = None
    #         session.add(season)

    #     self.active = True
    #     session.add(self)
    #     session.commit()
