from PyQt6.QtCore import (
    QModelIndex,
    QAbstractTableModel,
    QObject,
    Qt,
    QVariant,
    QSortFilterProxyModel,
)
from datetime import date
from sqlalchemy.sql import func
from sqlalchemy import case
from sqlalchemy.orm import Session
import db


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


class CustomerModelView(QAbstractTableModel):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        with Session(db.engine) as session:
            self.customers = [
                (
                    row[0].id,
                    row[0].name,
                    row[0].address,
                    row[0].birthday,
                    row[1],
                    row[0].phone_number,
                )
                for row in session.query(
                    db.Customer,
                    func.sum(
                        case(
                            (db.Season.active, db.Distilling.alcohol_volume_la),
                            else_=0.0,
                        )
                    ),
                )
                .outerjoin(db.Order, db.Customer.id == db.Order.customer_id)
                .outerjoin(db.Distilling, db.Distilling.order_id == db.Order.id)
                .outerjoin(db.Season, db.Season.id == db.Order.season_id)
                .group_by(db.Customer)
            ]
        self._headers = [
            "id",
            "Meno a priezvisko",
            "Adresa",
            "Dátum nar.",
            "la",
            "Tel. číslo",
        ]

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
