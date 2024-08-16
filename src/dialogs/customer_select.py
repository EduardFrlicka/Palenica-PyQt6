from PyQt6.QtWidgets import QDialog
from ui_py.customer_select_ui import Ui_CustomerSelect
from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QShowEvent
from sqlalchemy.orm import Session
import db
from datetime import datetime, date
from constants import DATE_FORMAT
from dialogs.alert import alert
from messages import DATABASE_OFFLINE

from models.customer_model import CustomerModelView, CustomerSortFilterModel
from models.delegates import date_delegate


class CustomerSelectDialog(QDialog, Ui_CustomerSelect):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.customer = None
        self.customer_is_new = False
        self.name = None
        self.address = None
        self.birthday = None
        self.phone_number = None
        self.setWindowState(Qt.WindowState.WindowMaximized)

    def loadData(self):
        self.customer_model = CustomerModelView(self)
        self.filter_model = CustomerSortFilterModel(self)
        self.filter_model.setSourceModel(self.customer_model)
        self.customer_table.setModel(self.filter_model)
        self.customer_table.resizeColumnsToContents()
        self.customer_table.setColumnHidden(0, True)
        self.customer_table.setItemDelegateForColumn(3, date_delegate)
        self.customer_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)

    def showEvent(self, a0: QShowEvent | None) -> None:
        res = super().showEvent(a0)
        if db.engine is None:
            alert(DATABASE_OFFLINE)
            return res
        self.loadData()
        return res

    def customer_selected(self, index: QModelIndex):
        customer_id = index.siblingAtColumn(0).data()
        # self.customer_model.customers[index.row()][0]
        print("selected", customer_id)
        with Session(db.engine) as session:
            self.customer = session.query(db.Customer).get(customer_id)
        self.accept()
        pass

    def customer_created(self):
        if db.engine is None:
            self.reject()
            return

        if self.name is None:
            alert("Chýba meno zákazníka")
            return
        if self.address is None:
            alert("Chýba adresa zákazníka")
            return
        if self.birthday is None:
            alert("Chýba dátum narodenia zákazníka")
            return

        if self.phone_number is None:
            self.phone_number = ""

        self.customer = db.Customer(self.name, self.address, self.birthday, self.phone_number)
        with Session(db.engine) as session:
            session.add(self.customer)
            session.commit()
            session.refresh(self.customer)

        self.customer_is_new = True
        print("created")
        self.accept()
        pass

    def name_edited(self, text: str):
        self.name = text
        self.filter_model.filterName(text)

    def birthday_edited(self, text: str):
        try:
            self.birthday = datetime.strptime(text.replace(" ", ""), DATE_FORMAT).date()
            self.filter_model.filterBirthday(self.birthday)
        except:
            self.filter_model.filterBirthday(None)
            pass

    def address_edited(self, text: str):
        self.address = text
        self.filter_model.filterAddress(text)

    def phone_number_edited(self, text: str):
        self.phone_number = text.replace(" ", "")
        self.filter_model.filterPhoneNumber(text)
