from .base import Base, STRING_LEN
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
import db


class Constant(Base):
    __tablename__ = "constant"
    id: Mapped[str] = mapped_column(String(STRING_LEN), primary_key=True)
    value: Mapped[float] = mapped_column(Float)

    def __init__(self, name: str, value: float):
        self.id = name
        self.value = value

    @staticmethod
    def get(name: str) -> float:
        with db.Session(db.engine) as session:
            return session.query(Constant).get(name).value
