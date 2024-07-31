from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
import db
import sys
import updater


app = QApplication(sys.argv)
main_window = MainWindow()

updater.update()

main_window.show()
app.exec()

sys.exit()
