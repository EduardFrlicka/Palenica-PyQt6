import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui_py.main_window_ui import Ui_MainWindow

class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()

        from tabs.create_distilling_tab import CreateDistillingTab
        from tabs.distillings_tab import DistillingsTab
        from tabs.seasons_tab import SeasonsTab

        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.tabWidget.clear()
        self.create_distilling_tab = CreateDistillingTab()
        self.tabWidget.addTab(self.create_distilling_tab, "Nová destilácia")

        self.distillings_tab = DistillingsTab()
        self.tabWidget.addTab(self.distillings_tab, "Destilácie")

        self.seasons_tab = SeasonsTab()
        self.tabWidget.addTab(self.seasons_tab, "Sezóny")


app = QApplication(sys.argv)

import updater
updater.check_and_perform_update()

import db

main_window = MainWindow()
main_window.show()
app.exec()

sys.exit()
