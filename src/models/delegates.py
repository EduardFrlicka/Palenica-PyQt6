from PyQt6.QtWidgets import QStyledItemDelegate
from datetime import date
from constants import DATE_FORMAT


class DateDelegate(QStyledItemDelegate):
    def displayText(self, value: date, _) -> str:
        return value.strftime(DATE_FORMAT)


date_delegate = DateDelegate()


class CostDelegate(QStyledItemDelegate):
    def displayText(self, value: float, _) -> str:
        return f"{value:.2f}"


cost_delegate = CostDelegate()
