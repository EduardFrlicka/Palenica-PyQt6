from ui_py.updater_window_ui import Ui_Updater
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt
from threading import Thread


class UpdaterWindow(Ui_Updater, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def set_progress(self, value: int):
        self.progressBar.setValue(value)


app = QApplication([])
window = UpdaterWindow()

window.show()

app.exec()
