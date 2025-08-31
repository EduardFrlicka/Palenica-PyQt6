from datetime import datetime
from PyQt6.QtWidgets import (
    QLineEdit,
    QTableWidgetItem,
    QTabBar,
    QPushButton,
)
from PyQt6.QtCore import QModelIndex, Qt
from constants import DATE_FORMAT
from dialogs.alert import alert
from ui_py.customers_tab_ui import Ui_CustomersTab
from models.delegates import date_delegate
from models.customer_model import CustomerModelView, CustomerSortFilterModel
import db


class CustomersTab(Ui_CustomersTab, QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.name = None
        self.address = None
        self.birthday = None
        self.phone_number = None
        self.season_id = None
        self.seasonSelect.enable_empty(True)

        self.loadData()

    def loadData(self):
        # season_id = db.get_active_season().id
        self.seasonSelect.seasonSelected
        self.customer_model = CustomerModelView(self.season_id, self)
        self.filter_model = CustomerSortFilterModel(self)
        self.filter_model.setSourceModel(self.customer_model)
        self.customer_table.setModel(self.filter_model)
        self.customer_table.resizeColumnsToContents()
        self.customer_table.setColumnHidden(0, True)
        self.customer_table.setItemDelegateForColumn(3, date_delegate)
        self.customer_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)

    # def customer_selected(self, index: QModelIndex):
    #     customer_id = index.siblingAtColumn(0).data()
    #     # self.customer_model.customers[index.row()][0]
    #     print("selected", customer_id)
    #     with db.get_session() as session:
    #         self.customer = session.query(db.Customer).get(customer_id)
    #     self.accept()
    #     pass

    def customer_created(self):
        if db.get_engine() is None:
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
        with db.get_session() as session:
            session.add(self.customer)
            session.commit()
            session.refresh(self.customer)

        self.customer_is_new = True
        print("created")
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

    def season_selected(self, season_id: int):
        self.season_id = season_id
        self.loadData()
