from .base import Base, STRING_LEN
from sqlalchemy import String, Float, Integer, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
import db


class CalculationConstants(Base):
    __tablename__ = "constants"
    timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    lower_tax: Mapped[float] = mapped_column(Float)
    full_tax: Mapped[float] = mapped_column(Float)
    lower_tax_la_limit: Mapped[float] = mapped_column(Float)
    vat_tax: Mapped[float] = mapped_column(Float)
    # cost per liter 50%
    service_cost: Mapped[float] = mapped_column(Float)
    
    def __init__(self, lower_tax: float, full_tax: float, lower_tax_la_limit: float, vat_tax: float, service_cost: float):
        self.lower_tax = lower_tax
        self.full_tax = full_tax
        self.lower_tax_la_limit = lower_tax_la_limit
        self.vat_tax = vat_tax
        self.service_cost = service_cost
        self.timestamp = datetime.now(timezone.utc)

    @staticmethod
    def get() -> "CalculationConstants":
        if db.get_engine() is None:
            return CalculationConstants(
                lower_tax=7.452,
                full_tax=14.904,
                lower_tax_la_limit=43,
                vat_tax=0.20,
                service_cost=8.2
            )

        with db.get_session() as session:
            constants = session.query(CalculationConstants).order_by(CalculationConstants.timestamp.desc()).first()
            if constants is None:
                constants = CalculationConstants(
                    lower_tax=7.452,
                    full_tax=14.904,
                    lower_tax_la_limit=43,
                    vat_tax=0.20,
                    service_cost=8.2
                )
                session.add(constants)
                session.commit()
                session.refresh(constants)
            # Detach the object from the session
            session.expunge(constants)
            return constants
