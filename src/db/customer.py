from .base import Base, STRING_LEN
from sqlalchemy import ForeignKey, Integer, String, Date, Float, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import date, datetime
import db


class Customer(Base):
    __tablename__ = "customer"
    id_seq = Sequence("customer_id_seq", start=1, increment=1)
    id: Mapped[int] = mapped_column(Integer, id_seq, primary_key=True)
    name: Mapped[str] = mapped_column(String(STRING_LEN))
    address: Mapped[str] = mapped_column(String(STRING_LEN))
    birthday: Mapped[date] = mapped_column(Date)
    phone_number: Mapped[str] = mapped_column(String(STRING_LEN))

    def __init__(self, name: str, adress: str, birthday: date, phone_number: str):
        self.name = name
        self.address = adress
        self.birthday = birthday
        self.phone_number = phone_number
