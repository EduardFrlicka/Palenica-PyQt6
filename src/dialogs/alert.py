from PyQt6.QtWidgets import QMessageBox


def alert(text: str):
    print("Alert: ", text)

    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Critical)
    msgBox.setText(text)
    msgBox.setWindowTitle("Chyba")
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.buttonClicked.connect(msgBox.clickedButton)

    msgBox.exec()

    if msgBox.clickedButton() != msgBox.button(QMessageBox.StandardButton.Ok):
        print("Alert was not closed with OK button.")
        raise Exception("Alert was not closed with OK button.")

def error(text: str):
    print("Error: ", text)

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
