from PyQt6.QtWidgets import QTabBar
from ui_py.distillings_tab_ui import Ui_DistillingsTab


class DistillingsTab(Ui_DistillingsTab, QTabBar):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
