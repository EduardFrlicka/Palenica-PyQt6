# import app

from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
import db
import sys
from datetime import datetime


# db.drop_all()
# db.create_all()
# db.populate()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()


# app.main_window.centralWidget().show()
# exit(app.app.exec())
