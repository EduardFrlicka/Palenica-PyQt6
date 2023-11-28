# Form implementation generated from reading ui file 'src/ui/customer_handler.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CustomerHandler(object):
    def setupUi(self, CustomerHandler):
        CustomerHandler.setObjectName("CustomerHandler")
        CustomerHandler.resize(1360, 312)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CustomerHandler.sizePolicy().hasHeightForWidth())
        CustomerHandler.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(CustomerHandler)
        self.verticalLayout.setObjectName("verticalLayout")
        self.select_buttons = QtWidgets.QWidget(parent=CustomerHandler)
        self.select_buttons.setObjectName("select_buttons")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.select_buttons)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.button_customer_select = QtWidgets.QPushButton(parent=self.select_buttons)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_customer_select.sizePolicy().hasHeightForWidth())
        self.button_customer_select.setSizePolicy(sizePolicy)
        self.button_customer_select.setObjectName("button_customer_select")
        self.horizontalLayout_2.addWidget(self.button_customer_select)
        self.button_customer_manual = QtWidgets.QPushButton(parent=self.select_buttons)
        self.button_customer_manual.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_customer_manual.sizePolicy().hasHeightForWidth())
        self.button_customer_manual.setSizePolicy(sizePolicy)
        self.button_customer_manual.setCheckable(False)
        self.button_customer_manual.setObjectName("button_customer_manual")
        self.horizontalLayout_2.addWidget(self.button_customer_manual)
        self.horizontalLayout_2.setStretch(0, 6)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addWidget(self.select_buttons)
        self.customerPreview = QtWidgets.QWidget(parent=CustomerHandler)
        self.customerPreview.setObjectName("customerPreview")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.customerPreview)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.vertical_name = QtWidgets.QVBoxLayout()
        self.vertical_name.setObjectName("vertical_name")
        self.label_name = QtWidgets.QLabel(parent=self.customerPreview)
        self.label_name.setObjectName("label_name")
        self.vertical_name.addWidget(self.label_name)
        self.le_name = QtWidgets.QLineEdit(parent=self.customerPreview)
        self.le_name.setObjectName("le_name")
        self.vertical_name.addWidget(self.le_name)
        self.horizontalLayout.addLayout(self.vertical_name)
        self.vertical_address = QtWidgets.QVBoxLayout()
        self.vertical_address.setObjectName("vertical_address")
        self.label_address = QtWidgets.QLabel(parent=self.customerPreview)
        self.label_address.setObjectName("label_address")
        self.vertical_address.addWidget(self.label_address)
        self.le_address = QtWidgets.QLineEdit(parent=self.customerPreview)
        self.le_address.setObjectName("le_address")
        self.vertical_address.addWidget(self.le_address)
        self.horizontalLayout.addLayout(self.vertical_address)
        self.vertical_birthday = QtWidgets.QVBoxLayout()
        self.vertical_birthday.setObjectName("vertical_birthday")
        self.label_birthday = QtWidgets.QLabel(parent=self.customerPreview)
        self.label_birthday.setObjectName("label_birthday")
        self.vertical_birthday.addWidget(self.label_birthday)
        self.le_birthday = QtWidgets.QLineEdit(parent=self.customerPreview)
        self.le_birthday.setObjectName("le_birthday")
        self.vertical_birthday.addWidget(self.le_birthday)
        self.horizontalLayout.addLayout(self.vertical_birthday)
        self.vertical_phone_number = QtWidgets.QVBoxLayout()
        self.vertical_phone_number.setObjectName("vertical_phone_number")
        self.label_phone_number = QtWidgets.QLabel(parent=self.customerPreview)
        self.label_phone_number.setObjectName("label_phone_number")
        self.vertical_phone_number.addWidget(self.label_phone_number)
        self.cb_phone_number = QtWidgets.QComboBox(parent=self.customerPreview)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cb_phone_number.sizePolicy().hasHeightForWidth())
        self.cb_phone_number.setSizePolicy(sizePolicy)
        self.cb_phone_number.setEditable(True)
        self.cb_phone_number.setDuplicatesEnabled(False)
        self.cb_phone_number.setObjectName("cb_phone_number")
        self.vertical_phone_number.addWidget(self.cb_phone_number)
        self.horizontalLayout.addLayout(self.vertical_phone_number)
        self.pushButton = QtWidgets.QPushButton(parent=self.customerPreview)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.customerPreview)
        self.la_preview = QtWidgets.QWidget(parent=CustomerHandler)
        self.la_preview.setObjectName("la_preview")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.la_preview)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_la_before = QtWidgets.QLabel(parent=self.la_preview)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_la_before.sizePolicy().hasHeightForWidth())
        self.label_la_before.setSizePolicy(sizePolicy)
        self.label_la_before.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_la_before.setObjectName("label_la_before")
        self.horizontalLayout_3.addWidget(self.label_la_before)
        self.le_la_before = QtWidgets.QLineEdit(parent=self.la_preview)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.le_la_before.sizePolicy().hasHeightForWidth())
        self.le_la_before.setSizePolicy(sizePolicy)
        self.le_la_before.setReadOnly(True)
        self.le_la_before.setObjectName("le_la_before")
        self.horizontalLayout_3.addWidget(self.le_la_before)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_la_after = QtWidgets.QLabel(parent=self.la_preview)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_la_after.sizePolicy().hasHeightForWidth())
        self.label_la_after.setSizePolicy(sizePolicy)
        self.label_la_after.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_la_after.setObjectName("label_la_after")
        self.horizontalLayout_3.addWidget(self.label_la_after)
        self.le_la_after = QtWidgets.QLineEdit(parent=self.la_preview)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.le_la_after.sizePolicy().hasHeightForWidth())
        self.le_la_after.setSizePolicy(sizePolicy)
        self.le_la_after.setReadOnly(True)
        self.le_la_after.setObjectName("le_la_after")
        self.horizontalLayout_3.addWidget(self.le_la_after)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.la_preview)

        self.retranslateUi(CustomerHandler)
        self.pushButton.clicked.connect(CustomerHandler.change_customer) # type: ignore
        self.button_customer_select.clicked.connect(CustomerHandler.select_customer) # type: ignore
        self.button_customer_manual.clicked.connect(CustomerHandler.manual_customer) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(CustomerHandler)

    def retranslateUi(self, CustomerHandler):
        _translate = QtCore.QCoreApplication.translate
        CustomerHandler.setWindowTitle(_translate("CustomerHandler", "Form"))
        self.button_customer_select.setText(_translate("CustomerHandler", "Zvoliť zákazníka"))
        self.button_customer_manual.setText(_translate("CustomerHandler", "Manuálne \n"
"zadať \n"
"zákazníka"))
        self.label_name.setText(_translate("CustomerHandler", "Meno a priezvisko:"))
        self.label_address.setText(_translate("CustomerHandler", "Adresa:"))
        self.label_birthday.setText(_translate("CustomerHandler", "Dátum nar.:"))
        self.label_phone_number.setText(_translate("CustomerHandler", "Tel. číslo:"))
        self.pushButton.setText(_translate("CustomerHandler", "Zmeniť\n"
"zákazníka"))
        self.label_la_before.setText(_translate("CustomerHandler", "Množstvo la pred pálením:"))
        self.label_la_after.setText(_translate("CustomerHandler", "Množstvo la po pálení:"))
