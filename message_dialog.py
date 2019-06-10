# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './message_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(659, 458)
        self.formLayout = QtWidgets.QFormLayout(Dialog)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.text = QtWidgets.QPlainTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.text.sizePolicy().hasHeightForWidth())
        self.text.setSizePolicy(sizePolicy)
        self.text.setReadOnly(True)
        self.text.setObjectName("text")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.text)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.message_id = QtWidgets.QLineEdit(Dialog)
        self.message_id.setReadOnly(True)
        self.message_id.setObjectName("message_id")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.message_id)
        self.message_time = QtWidgets.QLineEdit(Dialog)
        self.message_time.setReadOnly(True)
        self.message_time.setObjectName("message_time")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.message_time)
        self.message_type = QtWidgets.QLineEdit(Dialog)
        self.message_type.setReadOnly(True)
        self.message_type.setObjectName("message_type")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.message_type)
        self.message_title = QtWidgets.QLineEdit(Dialog)
        self.message_title.setReadOnly(True)
        self.message_title.setObjectName("message_title")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.message_title)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.client_ip = QtWidgets.QLineEdit(Dialog)
        self.client_ip.setObjectName("client_ip")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.client_ip)
        self.script_name = QtWidgets.QLineEdit(Dialog)
        self.script_name.setReadOnly(True)
        self.script_name.setObjectName("script_name")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.script_name)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "ID"))
        self.label_2.setText(_translate("Dialog", "Time"))
        self.label_3.setText(_translate("Dialog", "Message Type"))
        self.label_4.setText(_translate("Dialog", "Message"))
        self.label_5.setText(_translate("Dialog", "Title"))
        self.label_6.setText(_translate("Dialog", "Client IP"))
        self.label_7.setText(_translate("Dialog", "Script Name"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
