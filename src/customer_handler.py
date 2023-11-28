from PyQt6.QtWidgets import QWidget, QCompleter
from PyQt6.QtCore import pyqtSignal
from customer_select import CustomerSelectDialog
from ui_py.customer_handler_ui import Ui_CustomerHandler
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import db
from constants import DATE_FORMAT


class CustomerHandler(QWidget, Ui_CustomerHandler):
    la_changed = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setupUi(self)
        self.change_customer()

    def select_customer(self):
        customer_select = CustomerSelectDialog()
        if customer_select.exec():
            self.load_customer(customer_select.customer)
            self.setReadOnly(True)
            self.la_preview.show()
            self.customerPreview.show()
            self.select_buttons.hide()
        print("customer", self.customer)

    def change_customer(self):
        self.is_manual = False
        self.la_preview.hide()
        self.customerPreview.hide()
        self.select_buttons.show()
        self.customer = None
        self.la = None

    def manual_customer(self):
        self.is_manual = True
        self.setReadOnly(False)
        self.le_address.setText("")
        self.le_birthday.setText("")
        self.le_name.setText("")
        self.le_la_before.setText("")
        self.cb_phone_number.setEditText("")
        self.cb_phone_number.setCompleter(QCompleter())
        self.cb_phone_number.clear()

        self.la_preview.hide()
        self.customerPreview.show()
        self.select_buttons.hide()
        self.la = 0
        self.la_changed.emit()

    def manual_customer_edit_change(self):
        pass

    def new_customer_edit_change(self):
        pass

    def bind_edits(self, func):
        self.cb_phone_number.editTextChanged.connect(func)
        self.le_address.textEdited.connect(func)
        self.le_birthday.textEdited.connect(func)
        self.le_name.textEdited.connect(func)
        self.le_la_before.textEdited.connect(func)

    def load_customer(self, customer: db.Customer):
        self.customer = customer
        with Session(db.engine) as session:
            self.la = (
                session.query(func.sum(db.Distilling.alcohol_volume_la))
                .outerjoin(db.Order, db.Distilling.order_id == db.Order.id)
                .outerjoin(db.Customer, db.Customer.id == db.Order.customer_id)
                .group_by(db.Customer.id)
                .filter(db.Customer.id == customer.id)
                .first()
            )
            if self.la is None:
                self.la = 0
            else:
                self.la = self.la[0]

        self.le_address.setText(self.customer.address)
        self.le_birthday.setText(self.customer.birthday.strftime(DATE_FORMAT))
        self.le_name.setText(self.customer.name)
        self.le_la_before.setText(f"{self.la:.2f}")

        self.cb_phone_number.clear()
        self.cb_phone_number.addItem(self.customer.phone_number)
        self.cb_phone_number.setEditText(self.customer.phone_number)

        self.completer = QCompleter([self.customer.phone_number])
        self.cb_phone_number.setCompleter(self.completer)

        self.la_changed.emit()

    def setReadOnly(self, value: bool):
        self.le_address.setReadOnly(value)
        self.le_birthday.setReadOnly(value)
        self.le_name.setReadOnly(value)
