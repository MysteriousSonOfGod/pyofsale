# This Python file uses the following encoding: utf-8
import os

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

import sys
import sqlite3


class addOrEditCustomer_Ui(QtWidgets.QDialog):
    def __init__(self, customerId=None):
        super(addOrEditCustomer_Ui, self).__init__()
        self.customerId = customerId
        uic.loadUi('addOrEditCustomer/form.ui', self)
        self.conn = sqlite3.connect('pyofsaledb.db')
        self.cur = self.conn.cursor()

        if customerId is None:
            self.nameLineEdit.textChanged.connect(self.nameDbCheck)

        else:
            self.setPrefill()
            self.saveButton.setEnabled(True)
        self.saveButton.clicked.connect(self.saveCustomer)
        self.cancelButton.clicked.connect(lambda: self.close())
        rx = QRegExp("[0-9]*")
        self.phoneLineEdit.setValidator(QRegExpValidator(rx, self))

        self.show()

    def nameDbCheck(self):
        self.cur.execute("SELECT NAME FROM customers WHERE NAME LIKE '" + self.nameLineEdit.text() + "' LIMIT 1")
        queryReturn = self.cur.fetchone()
        if queryReturn is not None or self.nameLineEdit.text() == "":
            self.alreadyRegLabel.setText(
                """<html><head/><body><p><span style=" color:#ef2929;">This customer is already registered.</span></p></body></html>""")
            self.saveButton.setEnabled(False)
        else:
            self.alreadyRegLabel.setText("")
            self.saveButton.setEnabled(True)

    def setPrefill(self):
        self.cur.execute("SELECT NAME,EMAIL,PHONE,ADDRESS FROM customers WHERE CUSTOMID="+str(self.customerId))
        customerTuple = self.cur.fetchone()
        self.nameLineEdit.setText(customerTuple[0])
        self.emailLineEdit.setText(customerTuple[1])
        self.phoneLineEdit.setText(customerTuple[2])
        self.addressLineEdit.setText(customerTuple[3])

    def saveCustomer(self):
        if self.customerId is None:
            self.cur.execute(
                'INSERT INTO customers (NAME,EMAIL,PHONE,ADDRESS) VALUES("' + self.nameLineEdit.text() + '","'
                + self.emailLineEdit.text() + '","' + self.phoneLineEdit.text() + '","' + self.addressLineEdit.text()
                + '")')
        else:
            self.cur.execute('UPDATE customers SET NAME ="' + self.nameLineEdit.text() + '",EMAIL="' +
                             self.emailLineEdit.text() + '",PHONE="' + self.phoneLineEdit.text() + '",ADDRESS="' +
                             self.addressLineEdit.text() + '" WHERE CUSTOMID=' + str(self.customerId))

        self.conn.commit()
        self.close()

# app = QtWidgets.QApplication(sys.argv)
# window = addOrEditCustomer_Ui()
# app.exec_()
