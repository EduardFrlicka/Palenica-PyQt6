from PyQt6.QtWidgets import QWidget

import config as config_module
import messages
from config import config
from dialogs.alert import alert, info
from ui_py.config_tab_ui import Ui_ConfigTab


class ConfigTab(Ui_ConfigTab, QWidget):
    """Form for the settings in config.toml that users are expected to change."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Filling the form in loadData fires the change signals first.
        self.saved_values = None
        self.setupUi(self)
        self.loadData()

    def currentValues(self) -> dict:
        return {
            "updater": {
                "allow_updates": self.check_allow_updates.isChecked(),
                "url": self.edit_url.text().strip(),
                "timeout": self.spin_timeout.value(),
            },
            "printer": {
                "copies": self.spin_copies.value(),
            },
        }

    def loadData(self):
        self.check_allow_updates.setChecked(bool(config.get("updater", "allow_updates", default=True)))
        self.edit_url.setText(str(config.get("updater", "url", default="")))
        self.spin_timeout.setValue(int(config.get("updater", "timeout", default=10)))
        self.spin_copies.setValue(int(config.get("printer", "copies", default=1)))
        self.saved_values = self.currentValues()
        self.updateSaveButton()

    def updateSaveButton(self):
        edited = self.currentValues() != self.saved_values
        self.button_save.setEnabled(edited)
        self.button_reset.setEnabled(edited)

    def valueEdited(self):
        self.updateSaveButton()

    def saveData(self):
        values = self.currentValues()
        if not values["updater"]["url"]:
            alert(messages.CONFIG_URL_EMPTY)
            return

        try:
            config_module.save(values)
        except OSError as e:
            alert(messages.CONFIG_WRITE_FAILED.format(e))
            return

        self.saved_values = values
        self.updateSaveButton()
        info(messages.CONFIG_SAVED)
