from PyQt6.QtWidgets import QWidget, QVBoxLayout
from ui_py.resetable_line_edit_ui import Ui_ResetableLineEdit
from PyQt6.QtCore import pyqtSignal


class ResetableLineEdit(Ui_ResetableLineEdit, QWidget):
    textEdited = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)
        Ui_ResetableLineEdit.setupUi(self, self)
        self.reset_button.clicked.connect(self.reset_default)
        self.lineEdit.textEdited.connect(self.user_edited)
        self.default_value = None
        self.reset_default()

    def setDefault(self, value):
        if self.is_default:
            self._setEdit(value)
            self.value = value
        else:
            self.default_value = value

    def _setEdit(self, value):
        if value is None:
            self.lineEdit.setText("")
        if (isinstance(value, float)):
            self.lineEdit.setText(f"{value:.2f}")

    def collect(self, value_type: type):
        try:
            return value_type(self.lineEdit.text())
        except ValueError:
            return value_type()

    def user_edited(self):
        self.is_default = False
        self.reset_button.show()
        value = self.collect(float)
        if value is not None:
            self.value = value
        self.textEdited.emit()

    def reset_default(self):
        self.is_default = True
        self.value = self.default_value
        self._setEdit(self.default_value)
        self.reset_button.hide()
        self.textEdited.emit()
