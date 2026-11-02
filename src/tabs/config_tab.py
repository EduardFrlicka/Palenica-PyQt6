import tomllib

from PyQt6.QtWidgets import QWidget

import messages
from config import config_path
from dialogs.alert import alert, info
from ui_py.config_tab_ui import Ui_ConfigTab


class ConfigTab(Ui_ConfigTab, QWidget):
    """Plain text editor for config.toml.

    The text is checked to be valid TOML before it is written, so a typo
    cannot leave the application unable to start.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.label_path.setText(str(config_path))
        self.loadData()

    def loadData(self):
        try:
            text = config_path.read_text(encoding="utf-8")
        except OSError as e:
            alert(messages.CONFIG_READ_FAILED.format(e))
            text = ""
        self.saved_text = text
        self.text_config.setPlainText(text)
        self.updateSaveButton()

    def updateSaveButton(self):
        self.button_save.setEnabled(self.text_config.toPlainText() != self.saved_text)

    def valueEdited(self):
        self.updateSaveButton()

    def saveData(self):
        text = self.text_config.toPlainText()
        try:
            tomllib.loads(text)
        except tomllib.TOMLDecodeError as e:
            alert(messages.CONFIG_INVALID.format(e))
            return

        try:
            config_path.write_text(text, encoding="utf-8")
        except OSError as e:
            alert(messages.CONFIG_WRITE_FAILED.format(e))
            return

        self.saved_text = text
        self.updateSaveButton()
        info(messages.CONFIG_SAVED)
