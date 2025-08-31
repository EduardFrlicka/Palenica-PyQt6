from ui_py.seasons_tab_ui import Ui_SeasonsTab
from PyQt6.QtWidgets import QTabBar, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShowEvent
from models.seasons_model import SeasonModelView
from models.delegates import date_delegate, cost_delegate
from PyQt6.QtCore import QModelIndex
from dialogs.season_dialog import SeasonDialog


class SeasonsTab(Ui_SeasonsTab, QTabBar):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def showEvent(self, a0: QShowEvent | None) -> None:
        res = super().showEvent(a0)
        self.loadData()
        return res

    def loadData(self):
        self.season_model = SeasonModelView(self)
        self.table_seasons.setModel(self.season_model)
        self.table_seasons.setItemDelegateForColumn(1, date_delegate)
        self.table_seasons.setItemDelegateForColumn(2, date_delegate)
        self.table_seasons.setItemDelegateForColumn(5, cost_delegate)
        self.table_seasons.setColumnHidden(0, True)
        self.table_seasons.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.table_seasons.resizeColumnsToContents()
        pass

    def season_selected(self, index: QModelIndex):
        season_id = index.siblingAtColumn(0).data()
        dialog = SeasonDialog(season_id)
        dialog.exec()
        self.loadData()

    def season_create(self):
        dialog = SeasonDialog()
        dialog.exec()
        self.loadData()
