from .base import Base, STRING_LEN
from sqlalchemy import ForeignKey, Integer, String, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import date, datetime
import db


class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(STRING_LEN))
    address: Mapped[str] = mapped_column(String(STRING_LEN))
    birthday: Mapped[date] = mapped_column(Date)
    phone_number: Mapped[str] = mapped_column(String(STRING_LEN))

    def __init__(self, name: str, adress: str, birthday: date, phone_number: str ):
        self.name = name
        self.address = adress
        self.birthday = birthday
        self.phone_number = phone_number
