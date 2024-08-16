from .base import Base
from .production_line import ProductionLine
from .distilling import Distilling
from .customer import Customer
from .season import Season
from .order import Order
from .constant import Constant
from .queries import *


def __getattr__(name: str):
    if name == "engine":
        from .db_engine import engine

        return engine
