from .base import Base, STRING_LEN
from sqlalchemy import ForeignKey, Integer, Sequence, String, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
import db


class ProductionLine(Base):
    __tablename__ = "production_line"
    id_seq = Sequence('production_line_id_seq', start=1, increment=1)
    id: Mapped[int] = mapped_column(Integer, id_seq, primary_key=True)
    name: Mapped[str] = mapped_column(String(STRING_LEN), unique=True)

    def __init__(self, name: str):
        self.name = name
