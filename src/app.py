from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui_py.main_window_ui import Ui_MainWindow
from tabs.create_distilling_tab import CreateDistillingTab
from tabs.distillings_tab import DistillingsTab
import db
import sys


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.tabWidget.clear()
        self.create_distilling_tab = CreateDistillingTab()
        self.tabWidget.addTab(self.create_distilling_tab, "Nová destilácia")

        self.distillings_tab = DistillingsTab()
        self.tabWidget.addTab(self.distillings_tab, "Destilácie")


app = QApplication(sys.argv)
main_window = MainWindow()

import updater

updater.update()

main_window.show()
app.exec()

sys.exit()
