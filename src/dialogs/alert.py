from PyQt6.QtWidgets import QMessageBox


def alert(text: str):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Critical)
    msgBox.setText(text)
    msgBox.setWindowTitle("Chyba")
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.buttonClicked.connect(msgBox.clickedButton)

    msgBox.exec()