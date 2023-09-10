# Form implementation generated from reading ui file 'src/ui/customer_select.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CustomerSelect(object):
    def setupUi(self, CustomerSelect):
        CustomerSelect.setObjectName("CustomerSelect")
        CustomerSelect.resize(647, 433)
        self.verticalLayout = QtWidgets.QVBoxLayout(CustomerSelect)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.vertical_name = QtWidgets.QVBoxLayout()
        self.vertical_name.setObjectName("vertical_name")
        self.label_name = QtWidgets.QLabel(parent=CustomerSelect)
        self.label_name.setObjectName("label_name")
        self.vertical_name.addWidget(self.label_name)
        self.le_name = QtWidgets.QLineEdit(parent=CustomerSelect)
        self.le_name.setObjectName("le_name")
        self.vertical_name.addWidget(self.le_name)
        self.horizontalLayout.addLayout(self.vertical_name)
        self.vertical_address = QtWidgets.QVBoxLayout()
        self.vertical_address.setObjectName("vertical_address")
        self.label_address = QtWidgets.QLabel(parent=CustomerSelect)
        self.label_address.setObjectName("label_address")
        self.vertical_address.addWidget(self.label_address)
        self.le_address = QtWidgets.QLineEdit(parent=CustomerSelect)
        self.le_address.setObjectName("le_address")
        self.vertical_address.addWidget(self.le_address)
        self.horizontalLayout.addLayout(self.vertical_address)
        self.vertical_birthday = QtWidgets.QVBoxLayout()
        self.vertical_birthday.setObjectName("vertical_birthday")
        self.label_birthday = QtWidgets.QLabel(parent=CustomerSelect)
        self.label_birthday.setObjectName("label_birthday")
        self.vertical_birthday.addWidget(self.label_birthday)
        self.le_birthday = QtWidgets.QLineEdit(parent=CustomerSelect)
        self.le_birthday.setObjectName("le_birthday")
        self.vertical_birthday.addWidget(self.le_birthday)
        self.horizontalLayout.addLayout(self.vertical_birthday)
        self.vertical_phone_number = QtWidgets.QVBoxLayout()
        self.vertical_phone_number.setObjectName("vertical_phone_number")
        self.label_phone_number = QtWidgets.QLabel(parent=CustomerSelect)
        self.label_phone_number.setObjectName("label_phone_number")
        self.vertical_phone_number.addWidget(self.label_phone_number)
        self.le_phone_number = QtWidgets.QLineEdit(parent=CustomerSelect)
        self.le_phone_number.setObjectName("le_phone_number")
        self.vertical_phone_number.addWidget(self.le_phone_number)
        self.horizontalLayout.addLayout(self.vertical_phone_number)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.add_new_customer_button = QtWidgets.QPushButton(parent=CustomerSelect)
        self.add_new_customer_button.setObjectName("add_new_customer_button")
        self.verticalLayout.addWidget(self.add_new_customer_button)
        self.customer_table = QtWidgets.QTableView(parent=CustomerSelect)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.customer_table.setFont(font)
        self.customer_table.setSortingEnabled(True)
        self.customer_table.setObjectName("customer_table")
        self.customer_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.customer_table)

        self.retranslateUi(CustomerSelect)
        self.customer_table.doubleClicked['QModelIndex'].connect(CustomerSelect.customer_selected) # type: ignore
        self.add_new_customer_button.clicked.connect(CustomerSelect.customer_created) # type: ignore
        self.le_name.textEdited['QString'].connect(CustomerSelect.name_edited) # type: ignore
        self.le_address.textEdited['QString'].connect(CustomerSelect.address_edited) # type: ignore
        self.le_birthday.textEdited['QString'].connect(CustomerSelect.birthday_edited) # type: ignore
        self.le_phone_number.textEdited['QString'].connect(CustomerSelect.phone_number_edited) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(CustomerSelect)

    def retranslateUi(self, CustomerSelect):
        _translate = QtCore.QCoreApplication.translate
        CustomerSelect.setWindowTitle(_translate("CustomerSelect", "Dialog"))
        self.label_name.setText(_translate("CustomerSelect", "Meno a priezvisko:"))
        self.label_address.setText(_translate("CustomerSelect", "Adresa:"))
        self.label_birthday.setText(_translate("CustomerSelect", "Dátum nar.:"))
        self.label_phone_number.setText(_translate("CustomerSelect", "Tel. číslo:"))
        self.add_new_customer_button.setText(_translate("CustomerSelect", "Nový zákazník"))
