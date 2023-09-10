from .base import Base, STRING_LEN
from sqlalchemy import ForeignKey, Integer, String, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
import db


class ProductionLine(Base):
    __tablename__ = "production_line"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(STRING_LEN), unique=True)

    def __init__(self, name: str):
        self.name = name
