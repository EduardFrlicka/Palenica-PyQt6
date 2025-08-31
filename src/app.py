import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui_py.main_window_ui import Ui_MainWindow
import updater
import db
from dialogs.alert import error
from config import config


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()

        from tabs.create_distilling_tab import CreateDistillingTab
        from tabs.distillings_tab import DistillingsTab
        from tabs.customers_tab import CustomersTab
        from tabs.seasons_tab import SeasonsTab
        from tabs.constants_tab import ConstantsTab

        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.tabWidget.clear()
        self.create_distilling_tab = CreateDistillingTab()
        if "create_distilling" in config.get("main_window", "tabs", default=[]):
            self.tabWidget.addTab(self.create_distilling_tab, "Nová destilácia")

        self.distillings_tab = DistillingsTab()
        if "distillings" in config.get("main_window", "tabs", default=[]):
            self.tabWidget.addTab(self.distillings_tab, "Destilácie")

        self.seasons_tab = SeasonsTab()
        if "seasons" in config.get("main_window", "tabs", default=[]):
            self.tabWidget.addTab(self.seasons_tab, "Sezóny")

        self.customers_tab = CustomersTab()
        if "customers" in config.get("main_window", "tabs", default=[]):
            self.tabWidget.addTab(self.customers_tab, "Zákazníci")

        self.constants_tab = ConstantsTab()
        if "constants" in config.get("main_window", "tabs", default=[]):
            self.tabWidget.addTab(self.constants_tab, "Konštanty")


app = QApplication(sys.argv)

# if __name__ == "__main__":

updater.check_and_perform_update()


main_window = MainWindow()
main_window.show()
app.exec()
sys.exit()
