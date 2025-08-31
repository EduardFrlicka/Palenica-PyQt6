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
from sqlalchemy.orm import Session
import db


class OrderSortFilterModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self.production_line = None
        self.mark = None
        self.production_date = None
        self.name = None
        self.birthday: date | None = None
        self.season_id = None

    def filterMark(self, mark: str):
        self.mark = mark
        self.invalidateRowsFilter()

    def filterProductionLine(self, production_line: str):
        self.production_line = production_line
        self.invalidateRowsFilter()

    def filterProductionDate(self, production_date: date | None):
        self.production_date = production_date
        self.invalidateRowsFilter()

    def filterName(self, name: str):
        self.name = name.lower().strip().split()
        self.invalidateRowsFilter()

    def filterBirthday(self, birthday: date | None):
        if self.birthday != birthday:
            self.birthday = birthday
            self.invalidateRowsFilter()
        
    def filterSeason(self, season_id: int | None):
        if self.season_id != season_id:
            self.season_id = season_id
            self.invalidateRowsFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if self.season_id:
            season_id = self.sourceModel().index(source_row, 1).data()
            if season_id != self.season_id:
                return False
        
        if self.mark:
            mark = self.sourceModel().index(source_row, 2).data()
            if self.mark not in mark:
                return False

        if self.production_line:
            production_line = self.sourceModel().index(source_row, 3).data()
            if production_line != self.production_line:
                return False

        if self.production_date:
            production_date: date = self.sourceModel().index(source_row, 4).data()
            if production_date != self.production_date:
                return False

        if self.name:
            name = self.sourceModel().index(source_row, 5).data().lower()
            for substr in self.name:
                if substr not in name:
                    return False

        if self.birthday:
            birthday: date = self.sourceModel().index(source_row, 7).data()
            if self.birthday != birthday:
                return False
        
        return True

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        if left.data() != right.data():
            return left.data() < right.data()

        left_name = self.sourceModel().index(left.row(), 1).data()
        right_name = self.sourceModel().index(right.row(), 1).data()

        return left_name < right_name


class OrderModelView(QAbstractTableModel):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        with db.get_session() as session:
            self._data = [
                (
                    row[0].id,
                    row[2].id,
                    row[0].mark,
                    row[3].name,
                    row[0].production_date,
                    row[1].name,
                    row[1].address,
                    row[1].birthday,
                    row[4],
                )
                for row in session.query(
                    db.Order,
                    db.Customer,
                    db.Season,
                    db.ProductionLine,
                    func.sum(db.Distilling.alcohol_volume_la),
                )
                .outerjoin(db.Customer)
                .outerjoin(db.Season)
                .outerjoin(db.ProductionLine)
                .outerjoin(db.Distilling)
                .group_by(db.Order, db.Customer, db.Season, db.ProductionLine)
            ]

        self._headers = [
            "id",
            "season_id",
            "Číslo objednávky",
            "Kolóna",
            "Dátum výroby",
            "Meno a priezvisko",
            "Adresa",
            "Dátum nar.",
            "la",
        ]

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> QVariant:
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._data[index.row()]

            cell = row[index.column()]

            res = QVariant(cell)
            return res

    def rowCount(self, _: QModelIndex) -> int:
        return len(self._data)

    def columnCount(self, _: QModelIndex) -> int:
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self._headers[section]
        return super().headerData(section, orientation, role)
