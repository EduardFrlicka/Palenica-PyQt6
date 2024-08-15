from PyQt6.QtWidgets import QMessageBox


def alert(text: str):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Critical)
    msgBox.setText(text)
    msgBox.setWindowTitle("Chyba")
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.buttonClicked.connect(msgBox.clickedButton)

    msgBox.exec()


def error(text: str):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Critical)
    msgBox.setText(text)
    msgBox.setWindowTitle("Chyba")
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.buttonClicked.connect(msgBox.clickedButton)

    msgBox.exec()

    exit(1)


def warning(text: str):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Warning)
    msgBox.setText(text)
    msgBox.setWindowTitle("Varovanie")
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.buttonClicked.connect(msgBox.clickedButton)

    msgBox.exec()
