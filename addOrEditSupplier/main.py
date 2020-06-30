# This Python file uses the following encoding: utf-8
import os

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

import sys
import sqlite3


class addOrEditSupplier_Ui(QtWidgets.QDialog):
    def __init__(self, supplierId=None):
        super(addOrEditSupplier_Ui, self).__init__()
        self.supplierId = supplierId
        uic.loadUi('addOrEditSupplier/form.ui', self)
        self.conn = sqlite3.connect('pyofsaledb.db')
        self.cur = self.conn.cursor()

        if supplierId is None:
            self.nameLineEdit.textChanged.connect(self.nameDbCheck)

        else:
            self.setPrefill()
            self.saveButton.setEnabled(True)
        self.saveButton.clicked.connect(self.saveSupplier)
        self.cancelButton.clicked.connect(lambda: self.close())
        rx = QRegExp("[0-9]*")
        self.phoneLineEdit.setValidator(QRegExpValidator(rx, self))

        self.show()

    def nameDbCheck(self):
        self.cur.execute("SELECT NAME FROM suppliers WHERE NAME LIKE ? LIMIT 1",self.nameLineEdit.text(),)
        queryReturn = self.cur.fetchone()
        if queryReturn is not None or self.nameLineEdit.text() == "":
            self.alreadyRegLabel.setText(
                """<html><head/><body><p><span style=" color:#ef2929;">This supplier is already registered.</span></p></body></html>""")
            self.saveButton.setEnabled(False)
        else:
            self.alreadyRegLabel.setText("")
            self.saveButton.setEnabled(True)

    def setPrefill(self):
        self.cur.execute("SELECT NAME,EMAIL,PHONE,ADDRESS FROM suppliers WHERE SUPPID= ? ",(self.supplierId,))
        supplierTuple = self.cur.fetchone()
        self.nameLineEdit.setText(supplierTuple[0])
        self.emailLineEdit.setText(supplierTuple[1])
        self.phoneLineEdit.setText(supplierTuple[2])
        self.addressLineEdit.setText(supplierTuple[3])

    def saveSupplier(self):
        if self.supplierId is None:
            self.cur.execute("INSERT INTO suppliers (NAME,EMAIL,PHONE,ADDRESS) VALUES (?,?,?,?)",
                             (self.nameLineEdit.text(),
                              self.emailLineEdit.text(),
                              self.phoneLineEdit.text(),
                              self.addressLineEdit.text(),))
        else:
            self.cur.execute("UPDATE suppliers SET NAME = ? , EMAIL = ? , PHONE=? , ADDRESS=?, WHERE SUPPID=?",
                             (self.nameLineEdit.text(),self.emailLineEdit.text(),
                              self.phoneLineEdit.text(),self.addressLineEdit.text()
                              ,self.supplierId,))
        self.conn.commit()
        self.close()

# app = QtWidgets.QApplication(sys.argv)
# window = addOrEditSupplier_Ui()
# app.exec_()
