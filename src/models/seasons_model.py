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


class SeasonModelView(QAbstractTableModel):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        with db.get_session() as session:
            self._data = [
                (season.id, season.date_start, season.date_end, la, alcohol_volume, cost_sum)
                for (season, la, alcohol_volume, cost_sum) in (
                    session.query(
                        db.Season,
                        func.coalesce(func.sum(db.Distilling.alcohol_volume_la), 0.0),
                        func.coalesce(func.sum(db.Distilling.alcohol_volume), 0.0),
                        func.coalesce(func.sum(db.Order.cost_sum), 0.0),
                    )
                    .outerjoin(db.Order, onclause=db.Order.season_id == db.Season.id)
                    .outerjoin(db.Distilling, onclause=db.Distilling.order_id == db.Order.id)
                    .group_by(db.Season)
                    .all()
                )
            ]

        self._headers = [
            "id",
            "Začiatok",
            "Koniec",
            "Spolu la",
            "Spolu litrov",
            "Spolu suma",
        ]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> QVariant:
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._data[index.row()]
            cell = row[index.column()]
            return QVariant(cell)

        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> QVariant:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return QVariant(self._headers[section])

        return QVariant()
