from PyQt6.QtWidgets import QDialog, QStyledItemDelegate
from ui_py.customer_select_ui import Ui_CustomerSelect
from PyQt6.QtCore import QModelIndex, QAbstractTableModel, QObject, Qt, QVariant, QSortFilterProxyModel
from PyQt6.QtGui import QShowEvent
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import db
from datetime import datetime, date
from constants import DATE_FORMAT
from alert import alert


class CustomerSortFilterModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self.name = None
        self.address = None
        self.number = None
        self.birthday: date | None = None

    def filterName(self, name: str):
        self.name = name.lower().strip().split()
        self.invalidateRowsFilter()

    def filterAddress(self, address: str):
        self.address = address.lower().strip().split()
        self.invalidateRowsFilter()

    def filterBirthday(self, birthday: date | None):
        if self.birthday != birthday:
            self.birthday = birthday
            self.invalidateRowsFilter()

    def filterPhoneNumber(self, number: str):
        self.number = number.lower().replace(" ", "")
        self.invalidateRowsFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if self.name:
            name = self.sourceModel().index(source_row, 1).data().lower()
            for substr in self.name:
                if substr not in name:
                    return False

        if self.address:
            address = self.sourceModel().index(source_row, 2).data().lower()
            for substr in self.address:
                if substr not in address:
                    return False

        if self.number:
            phone_number = self.sourceModel().index(source_row, 5).data().lower()
            if self.number not in phone_number:
                return False

        if self.birthday:
            birthday: date = self.sourceModel().index(source_row, 3).data()
            if self.birthday != birthday:
                return False

        return True

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        if left.data() != right.data():
            return left.data() < right.data()

        left_name = self.sourceModel().index(left.row(), 1).data()
        right_name = self.sourceModel().index(right.row(), 1).data()

        return left_name < right_name


class DateDelegate(QStyledItemDelegate):
    def displayText(self, value: date, _) -> str:
        return value.strftime(DATE_FORMAT)


class CustomerModelView(QAbstractTableModel):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        with Session(db.engine) as session:
            self.customers = [(row[0].id, row[0].name, row[0].address, row[0].birthday, row[1], row[0].phone_number) for row in session.query(db.Customer, func.sum(
                db.Distilling.alcohol_volume_la)).outerjoin(db.Order, db.Customer.id == db.Order.customer_id).outerjoin(db.Distilling, db.Distilling.order_id == db.Order.id).group_by(db.Customer)]
        self._headers = ["id", "Meno a priezvisko",
                         "Adresa", "Dátum nar.", "la", "Tel. číslo"]

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> QVariant:
        if role == Qt.ItemDataRole.DisplayRole:

            row = self.customers[index.row()]

            cell = row[index.column()]

            res = QVariant(cell)
            return res

    def rowCount(self, _: QModelIndex) -> int:
        return len(self.customers)

    def columnCount(self, _: QModelIndex) -> int:
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return super().headerData(section, orientation, role)


class CustomerSelectDialog(QDialog, Ui_CustomerSelect):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.customer = None
        self.customer_is_new = False
        self.name = None
        self.address = None
        self.birthday = None
        self.phone_number = None
        self.setWindowState(Qt.WindowState.WindowMaximized)

    def loadData(self):
        self.customer_model = CustomerModelView(self)
        self.filter_model = CustomerSortFilterModel(self)
        self.filter_model.setSourceModel(self.customer_model)
        self.customer_table.setModel(self.filter_model)
        self.customer_table.resizeColumnsToContents()
        self.customer_table.setColumnHidden(0, True)
        date_delegate = DateDelegate(self.customer_table)
        self.customer_table.setItemDelegateForColumn(3, date_delegate)
        self.customer_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)

    def showEvent(self, a0: QShowEvent | None) -> None:
        res = super().showEvent(a0)
        self.loadData()
        return res

    def customer_selected(self, index: QModelIndex):
        customer_id = index.siblingAtColumn(0).data()
        # self.customer_model.customers[index.row()][0]
        print("selected", customer_id)
        with Session(db.engine) as session:
            self.customer = session.query(db.Customer).get(customer_id)
        self.accept()
        pass

    def customer_created(self):
        if self.name is None:
            alert("name is missing")
            return
        if self.address is None:
            alert("address is missing")
            return
        if self.birthday is None:
            alert("birthday is missing")
            return
        if self.phone_number is None:
            alert("phone_number is missing")
            return

        self.customer = db.Customer(
            self.name, self.address, self.birthday, self.phone_number)
        with Session(db.engine) as session:
            session.add(self.customer)
            session.commit()
            session.refresh(self.customer)

        self.customer_is_new = True
        print("created")
        self.accept()
        pass

    def name_edited(self, text: str):
        self.name = text
        self.filter_model.filterName(text)

    def birthday_edited(self, text: str):
        try:
            self.birthday = datetime.strptime(
                text.replace(" ", ""), DATE_FORMAT).date()
            self.filter_model.filterBirthday(self.birthday)
        except:
            self.filter_model.filterBirthday(None)
            pass

    def address_edited(self, text: str):
        self.address = text
        self.filter_model.filterAddress(text)

    def phone_number_edited(self, text: str):
        self.phone_number = text.replace(" ", "")
        self.filter_model.filterPhoneNumber(text)
