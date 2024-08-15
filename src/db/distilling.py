from .base import Base, STRING_LEN
from sqlalchemy import ForeignKey, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
import db
from sqlalchemy import Engine


class Distilling(Base):
    __tablename__ = "distilling"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ferment_volume: Mapped[float] = mapped_column(Float)
    ferment_type: Mapped[str] = mapped_column(String(STRING_LEN))
    alcohol_volume: Mapped[float] = mapped_column(Float)
    alcohol_percentage: Mapped[float] = mapped_column(Float)
    alcohol_temperature: Mapped[float] = mapped_column(Float)
    alcohol_percentage_at_20: Mapped[float] = mapped_column(Float)
    alcohol_volume_la: Mapped[float] = mapped_column(Float)
    lower_tax: Mapped[float] = mapped_column(Float)
    full_tax: Mapped[float] = mapped_column(Float)
    sum_tax: Mapped[float] = mapped_column(Float)

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))

    def __init__(
        self,
        ferment_volume: float,
        ferment_type: str,
        alcohol_volume: float,
        alcohol_percentage: float,
        alcohol_temperature: float,
        alcohol_percentage_at_20: float,
        alcohol_volume_la: float,
        lower_tax: float,
        full_tax: float,
        sum_tax: float,
    ):

        self.ferment_volume = ferment_volume
        self.ferment_type = ferment_type
        self.alcohol_volume = alcohol_volume
        self.alcohol_percentage = alcohol_percentage
        self.alcohol_temperature = alcohol_temperature
        self.alcohol_percentage_at_20 = alcohol_percentage_at_20
        self.alcohol_volume_la = alcohol_volume_la
        self.lower_tax = lower_tax
        self.full_tax = full_tax
        self.sum_tax = sum_tax
