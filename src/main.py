# import app

from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
import db
import sys
from datetime import datetime

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()
