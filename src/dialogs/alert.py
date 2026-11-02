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


def confirm(text: str, accept_text: str, reject_text: str) -> bool:
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Warning)
    msgBox.setText(text)
    msgBox.setWindowTitle("Varovanie")
    accept_button = msgBox.addButton(accept_text, QMessageBox.ButtonRole.AcceptRole)
    reject_button = msgBox.addButton(reject_text, QMessageBox.ButtonRole.RejectRole)
    msgBox.setDefaultButton(reject_button)
    msgBox.setEscapeButton(reject_button)

    msgBox.exec()

    return msgBox.clickedButton() == accept_button


def info(text: str):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Icon.Information)
    msgBox.setText(text)
    msgBox.setWindowTitle("Informácia")
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)

    msgBox.exec()
