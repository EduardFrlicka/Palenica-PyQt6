from .base import Base
from sqlalchemy import ForeignKey, Integer, String, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import date, datetime
import db


class PhoneNumber(Base):
    __tablename__ = "phone_number"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer: Mapped["Customer"] = relationship(back_populates="phone_numbers")

    def __init__(self, number, customer=None):
        self.number = number
        if customer:
            self.customer = customer


class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    birthday: Mapped[date] = mapped_column(Date)
    phone_numbers: Mapped[List["PhoneNumber"]
                          ] = relationship(back_populates="customer")

    def __init__(self, name: str, adress: str, birthday: date, phone_numbers: list[str | PhoneNumber] | str = None):
        self.name = name
        self.address = adress
        self.birthday = birthday

        if phone_numbers:
            if isinstance(phone_numbers, list):
                for phone_number in phone_numbers:
                    if isinstance(phone_number, str):
                        self.phone_numbers.append(PhoneNumber(phone_number))
                    if isinstance(phone_number, PhoneNumber):
                        self.phone_numbers.append(phone_number)
            if isinstance(phone_numbers, str):
                self.phone_numbers.append(PhoneNumber(phone_numbers))
