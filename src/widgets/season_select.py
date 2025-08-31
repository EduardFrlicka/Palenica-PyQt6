from ui_py.season_select_widget_ui import Ui_SeasonSelectCB
from PyQt6.QtWidgets import QWidget
import db
from PyQt6.QtCore import pyqtSignal


class SeasonSelect(QWidget, Ui_SeasonSelectCB):
    seasonSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.items = db.get_all_seasons()
        self.comboBox.addItems([f"{season.to_string()}" for season in self.items])
        self.enabled_empty = False

        if db.get_active_season() is not None:
            active_season = db.get_active_season()
            index = self.comboBox.findText(active_season.to_string())
            if index != -1:
                self.comboBox.setCurrentIndex(index)

    def cbChanged(self, index: int):
        if index < 0 or index >= len(self.items):
            return
        selected_season = self.items[index]
        self.seasonSelected.emit(selected_season.id if selected_season else -1)

    def update_combo(self):
        self.items = db.get_all_seasons()
        if self.enabled_empty:
            self.items.insert(0, None)

        self.comboBox.clear()
        self.comboBox.addItems([f"{season.to_string()}" if season else "---" for season in self.items])

        if self.enabled_empty:
            self.comboBox.setCurrentIndex(0)
            return

        if db.get_active_season() is not None:
            active_season = db.get_active_season()
            index = self.comboBox.findText(active_season.to_string())
            if index != -1:
                self.comboBox.setCurrentIndex(index)

    def enable_empty(self, enable: bool):
        self.enabled_empty = enable
        self.update_combo()
