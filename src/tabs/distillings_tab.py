from PyQt6.QtWidgets import QTabBar
from ui_py.distillings_tab_ui import Ui_DistillingsTab
from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QShowEvent
from sqlalchemy.orm import Session
import db
from datetime import datetime, date
from constants import DATE_FORMAT
from models.order_model import OrderModelView, OrderSortFilterModel
from models.delegates import date_delegate


class DistillingsTab(Ui_DistillingsTab, QTabBar):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def showEvent(self, a0: QShowEvent | None) -> None:
        res = super().showEvent(a0)
        self.loadData()
        return res

    def loadData(self):
        self.order_model = OrderModelView(self)
        self.filter_model = OrderSortFilterModel(self)
        self.filter_model.setSourceModel(self.order_model)
        self.order_table.setModel(self.filter_model)
        self.order_table.setColumnHidden(0, True)
        self.order_table.setColumnHidden(1, True)
        self.order_table.setItemDelegateForColumn(4, date_delegate)
        self.order_table.setItemDelegateForColumn(7, date_delegate)
        self.order_table.sortByColumn(2, Qt.SortOrder.AscendingOrder)
        self.order_table.resizeColumnsToContents()

    def order_selected(self, index: QModelIndex):
        order_id = index.siblingAtColumn(0).data()
        print("selected", order_id)
        with Session(db.engine) as session:
            self.order = session.query(db.Order).get(order_id)

    def mark_edited(self, text: str):
        self.filter_model.filterMark(text)

    def production_line_selected(self, text: str):
        self.filter_model.filterProductionLine(text)

    def production_date_edited(self, text: str):
        formats = [
            ("%d", "my"),
            ("%d.", "my"),
            ("%d.%m", "y"),
            ("%d.%m.", "y"),
            ("%d.%m.%Y", ""),
        ]
        production_date = None

        for date_format, mode in formats:
            try:
                production_date = datetime.strptime(text, date_format).date()

                if "m" in mode:
                    production_date = production_date.replace(
                        month=datetime.now().month,
                    )
                if "y" in mode:
                    production_date = production_date.replace(
                        year=datetime.now().year,
                    )

                break
            except ValueError:
                continue

        self.filter_model.filterProductionDate(production_date)

    def name_edited(self, text: str):
        self.filter_model.filterName(text)

    def birthday_edited(self, text: str):
        try:
            birthday = datetime.strptime(text.replace(" ", ""), DATE_FORMAT).date()
        except ValueError:
            birthday = None

        self.filter_model.filterBirthday(birthday)
