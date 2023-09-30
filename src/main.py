# import app

from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
import db
import sys
import updater

updater.update()

# db.drop_all()
# db.create_all()
# db.populate()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()
