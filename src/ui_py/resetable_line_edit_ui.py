# Form implementation generated from reading ui file 'src/ui/resetable_line_edit.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ResetableLineEdit(object):
    def setupUi(self, ResetableLineEdit):
        ResetableLineEdit.setObjectName("ResetableLineEdit")
        ResetableLineEdit.resize(202, 48)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ResetableLineEdit)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(parent=ResetableLineEdit)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.lineEdit.setFont(font)
        self.lineEdit.setInputMask("")
        self.lineEdit.setPlaceholderText("")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.reset_button = QtWidgets.QPushButton(parent=ResetableLineEdit)
        self.reset_button.setEnabled(True)
        self.reset_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/png/undo_icon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.reset_button.setIcon(icon)
        self.reset_button.setObjectName("reset_button")
        self.horizontalLayout.addWidget(self.reset_button)

        self.retranslateUi(ResetableLineEdit)
        QtCore.QMetaObject.connectSlotsByName(ResetableLineEdit)

    def retranslateUi(self, ResetableLineEdit):
        _translate = QtCore.QCoreApplication.translate
        ResetableLineEdit.setWindowTitle(_translate("ResetableLineEdit", "Form"))
