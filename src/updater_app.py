from ui_py.updater_window_ui import Ui_Updater
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt
from threading import Thread
import updater


class UpdaterWindow(Ui_Updater, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def set_progress(self, value: int | float):
        if isinstance(value, float):
            value = int(value * 100)
        
        self.progressBar.setValue(value)


app = QApplication([])
window = UpdaterWindow()


def main():
    def finished():
        window.pushButton.setEnabled(True)
        window.label.setText("Hotovo")
        window.progressBar.hide()

    window.show()

    thread = Thread(
        target=updater.extract_update,
        args=(window.set_progress, finished),
    )
    thread.start()

    app.exec()


if __name__ == "__main__":
    main()
