from datetime import datetime
from PyQt6.QtWidgets import (
    QTabBar,
)
from constants import DATE_FORMAT
from dialogs.alert import alert
from ui_py.constants_tab_ui import Ui_ConstantsTab
import db


class ConstantsTab(Ui_ConstantsTab, QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.rle_full_tax.float_decimals = 3
        self.rle_lower_tax.float_decimals = 3
        self.rles = [
            self.rle_service_cost,
            self.rle_full_tax,
            self.rle_lower_tax,
            self.rle_la_limit,
            self.rle_vat_tax,
        ]
        self.loadData()

    def loadData(self):
        current_constants = db.CalculationConstants.get()
        self.rle_service_cost.setDefault(current_constants.service_cost)
        self.rle_full_tax.setDefault(current_constants.full_tax)
        self.rle_lower_tax.setDefault(current_constants.lower_tax)
        self.rle_la_limit.setDefault(current_constants.lower_tax_la_limit)
        self.rle_vat_tax.setDefault(current_constants.vat_tax * 100)
        self.updateSaveButton()

    def updateSaveButton(self):
        edited = False
        for rle in self.rles:
            if not rle.is_default:
                edited = True
                break

        self.button_save.setEnabled(edited)
        if not edited:
            self.button_save.setStyleSheet("color: red;")
        else:
            self.button_save.setStyleSheet("")


    def valueEdited(self):
        self.updateSaveButton()

    def saveData(self):
        new_constants = db.CalculationConstants(
            service_cost=self.rle_service_cost.value,
            full_tax=self.rle_full_tax.value,
            lower_tax=self.rle_lower_tax.value,
            lower_tax_la_limit=self.rle_la_limit.value,
            vat_tax=self.rle_vat_tax.value / 100,
        )

        with db.get_session() as session:
            session.add(new_constants)
            session.commit()
        
        self.loadData()
        for rle in self.rles:
            rle.reset_default()

