from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal
from ui_py.distilling_input_ui import Ui_distilling_input
import calculations
import db
from dialogs.alert import alert
import messages


class DistillingInput(Ui_distilling_input, QWidget):
    tax_edited = pyqtSignal()
    la_edited = pyqtSignal()

    def __init__(self, parent: QWidget, calculation_constants: db.CalculationConstants):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.delete_line_button.clicked.connect(self.remove_self)
        self.customer_la = 0

        self.ferment_volume = None
        self.ferment_type = None
        self.alcohol_volume = None
        self.alcohol_percentage = None
        self.alcohol_temperature = None
        self.alcohol_percentage_at_20 = 0
        self.alcohol_volume_la = 0
        self.lower_tax = None
        self.full_tax = None
        self.sum_tax = 0
        self.calculation_constants = calculation_constants

    def remove_self(self):
        layout_distilling_inputs = self.parent().findChild(
            QVBoxLayout, name="layout_distilling_inputs"
        )
        layout_distilling_inputs.removeWidget(self)
        self.alcohol_volume_la = 0
        self.la_edited.emit()

    def update_tax(self):
        if self.customer_la is None:
            return

        breakdown = calculations.excise_tax(
            self.customer_la,
            self.alcohol_volume_la,
            self.calculation_constants.lower_tax,
            self.calculation_constants.full_tax,
            self.calculation_constants.lower_tax_la_limit,
        )

        tax_updated = False

        if self.lower_tax != breakdown.lower:
            tax_updated = True
            self.lower_tax = breakdown.lower
            self.write_tax_edit(self.edit_lower_tax, self.lower_tax)

        if self.full_tax != breakdown.full:
            tax_updated = True
            self.full_tax = breakdown.full
            self.write_tax_edit(self.edit_full_tax, self.full_tax)

        if tax_updated:
            self.sum_tax = breakdown.total
            self.write_tax_edit(self.edit_sum_tax, self.sum_tax)
            self.tax_edited.emit()

    def update_values(self):
        if not self.collect_all():
            return

        self.alcohol_percentage_at_20 = calculations.percentage_at_20(
            self.alcohol_percentage, self.alcohol_temperature
        )
        self.write_edit(
            self.edit_alcohol_percentage_at_20, self.alcohol_percentage_at_20 * 100
        )

        new_alcohol_volume_la = calculations.litres_absolute(
            self.alcohol_percentage_at_20, self.alcohol_volume
        )

        if new_alcohol_volume_la != self.alcohol_volume_la:
            self.alcohol_volume_la = new_alcohol_volume_la
            self.write_edit(self.edit_alcohol_volume_la, self.alcohol_volume_la)
            self.update_tax()
            self.la_edited.emit()

    @staticmethod
    def write_edit(edit: QLineEdit, value):
        if isinstance(value, (float, int)):
            edit.setText(f"{value:0.2f}")

    @staticmethod
    def write_tax_edit(edit: QLineEdit, value):
        if isinstance(value, (float, int)):
            edit.setText(f"{value:0.2f}")

    def get_object(self):
        if self.ferment_volume is None:
            alert(messages.MISSING_INPUT.format("Množstvo kvasu"))
            return
        if self.ferment_type is None:
            alert(messages.MISSING_INPUT.format("Druh kvasu"))
            return
        if self.alcohol_volume is None:
            alert(messages.MISSING_INPUT.format("Množstvo destilátu"))
            return
        if self.alcohol_percentage is None:
            alert(messages.MISSING_INPUT.format("Objemové %"))
            return
        if self.alcohol_temperature is None:
            alert(messages.MISSING_INPUT.format("Teplota"))
            return
        if self.alcohol_percentage_at_20 == 0:
            alert(messages.ZERO_VALUE.format("Objemové percento pri 20˚C"))
            return
        if self.alcohol_volume_la == 0:
            alert(messages.ZERO_VALUE.format("Množstvo la"))
            return
        if self.lower_tax is None:
            alert(messages.INTERNAL_ERROR)
            return
        if self.full_tax is None:
            alert(messages.INTERNAL_ERROR)
            return
        if self.sum_tax == 0:
            alert(messages.MISSING_INPUT.format("Suma dane"))
            return
        return db.Distilling(
            self.ferment_volume,
            self.ferment_type,
            self.alcohol_volume,
            self.alcohol_percentage,
            self.alcohol_temperature,
            self.alcohol_percentage_at_20,
            self.alcohol_volume_la,
            self.lower_tax,
            self.full_tax,
            self.sum_tax,
        )

    def collect_all(self) -> bool:
        self.ferment_volume = self.collect_edit(self.edit_ferment_volume, float)
        if self.ferment_volume is None:
            self.ferment_volume = 0

        self.ferment_type = self.collect_edit(self.edit_ferment_type, str)
        if self.ferment_type is None:
            return False

        self.alcohol_volume = self.collect_edit(self.edit_alcohol_volume, float)
        if self.alcohol_volume is None:
            return False

        self.alcohol_percentage = self.collect_edit(self.edit_alcohol_percentage, float)
        if self.alcohol_percentage is None:
            return False

        self.alcohol_temperature = self.collect_edit(
            self.edit_alcohol_temperature, float
        )
        if self.alcohol_temperature is None:
            return False

        return True

    def collect_edit(self, edit: QLineEdit, value_type: type) -> float:
        try:
            text = edit.text()
            if value_type == float:
                text = text.replace(",", ".")
            return value_type(text)
        except ValueError:
            return None
