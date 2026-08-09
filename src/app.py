import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from ui_py.main_window_ui import Ui_MainWindow
import updater
import db
import messages
from dialogs.alert import error
from dialogs.splash import StartupSplash
from config import config


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, progress=lambda text: None):
        super().__init__()

        from tabs.create_distilling_tab import CreateDistillingTab
        from tabs.distillings_tab import DistillingsTab
        from tabs.customers_tab import CustomersTab
        from tabs.seasons_tab import SeasonsTab
        from tabs.constants_tab import ConstantsTab

        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        tabs = [
            ("create_distilling", "create_distilling_tab", "Nová destilácia", CreateDistillingTab),
            ("distillings", "distillings_tab", "Destilácie", DistillingsTab),
            ("seasons", "seasons_tab", "Sezóny", SeasonsTab),
            ("customers", "customers_tab", "Zákazníci", CustomersTab),
            ("constants", "constants_tab", "Konštanty", ConstantsTab),
        ]
        enabled_tabs = config.get("main_window", "tabs", default=[])

        self.tabWidget.clear()
        for config_name, attribute_name, title, tab_class in tabs:
            progress(messages.STARTUP_LOADING_TAB.format(title))
            tab = tab_class()
            setattr(self, attribute_name, tab)
            if config_name in enabled_tabs:
                self.tabWidget.addTab(tab, title)


def main() -> int:
    app = QApplication(sys.argv)

    splash = StartupSplash()
    splash.show()
    splash.message(messages.STARTUP_STARTING)

    splash.message(messages.STARTUP_CHECKING_UPDATES)
    if updater.check_and_perform_update(on_download_start=splash.hide):
        # The updater has taken over and will start us again once it is done.
        return 0

    # Connect up front so the wait on the hosted database gets its own message
    # instead of hiding inside the first tab that queries it.
    splash.message(messages.STARTUP_CONNECTING_DATABASE)
    db.get_engine()

    main_window = MainWindow(progress=splash.message)
    splash.message(messages.STARTUP_DONE)
    main_window.show()
    splash.finish(main_window)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
