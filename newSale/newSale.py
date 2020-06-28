
from PyQt5.QtGui import *

from PyQt5 import QtCore, QtGui, QtWidgets,uic
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtCore import *

from PyQt5.QtWidgets import *
import sqlite3
from decimal import Decimal as D

import sys

class Ui_newSaleWin(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_newSaleWin, self).__init__()
        uic.loadUi('newSale/newSale.ui', self)
        self.data = []

        # self.includeBtn.clicked.connect()
        self.setUpConnect()
        self.setCompleter()
        self.setCustomerCompleter()
        self.input = self.findChild(QtWidgets.QLineEdit, 'input')
        self.insertItemsTable()
        self.cancelButton.clicked.connect(lambda: self.close())
        self.includeBtn.clicked.connect(self.addItem)
        self.includeBtn.clicked.connect(self.searchLineEdit.setFocus)
        self.saveButton.clicked.connect(lambda: self.finishSale(0))
        self.customerLineEdit.editingFinished.connect(self.setCustomer)
        self.finButton.clicked.connect(lambda: self.finishSale(1))
        self.deleteBtn.clicked.connect(self.deleteItem)

        self.searchLineEdit.editingFinished.connect(self.setPrice)
        self.quantSpinbox.setKeyboardTracking(False)

        self.show()

    def setUpConnect(self):
        self.conn = sqlite3.connect('pyofsaledb.db')
        self.cur = self.conn.cursor()
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("pyofsaledb.db")
        self.db.open()

    def setPrice(self):
        if self.searchLineEdit.text() != '':
            self.cur.execute("SELECT PRICE FROM products WHERE DESC LIKE '" + self.searchLineEdit.text() + "%'")
            itemPrice = self.cur.fetchone()[0]
            self.doubleSpinBox.setValue(float(itemPrice))
            self.searchLineEdit.returnPressed.connect(lambda: self.quantSpinbox.setFocus())

    def insertItemsTable(self):
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(len(self.data))

        self.tableWidget.setHorizontalHeaderLabels(['Quant', 'Desc', 'Price'])
        for row in range(len(self.data)):
            self.cur.execute("SELECT DESC FROM products WHERE PRODID LIKE '" + str((self.data[row][1])) + "%'")
            itemDesc = self.cur.fetchone()[0]
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str((self.data[row][0]))))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(itemDesc)))
            self.tableWidget.setItem(row, 2, QTableWidgetItem((self.data[row][2])))

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        itemsSum = 0
        for row in self.data:
            itemTotal=D(D(row[0])*D(row[2]))
            itemsSum = itemTotal + itemsSum
        self.itemsSum=itemsSum
        self.tableWidget.clearSelection()

        if itemsSum>0:
            self.totalLabel.setText("Total: "+str(self.itemsSum))

        self.tableWidget.clearSelection()
        if self.alphaOrderCheck.isChecked():
            self.tableWidget.sortByColumn(1, Qt.AscendingOrder)

    def setCustomer(self):
        if self.customerLineEdit.text() is not None:
            self.cur.execute('SELECT CUSTOMID FROM customers WHERE NAME LIKE "' + str(self.customerLineEdit.text()) + '"')
            self.customId = self.cur.fetchone()[0]
        else:
            self.customId=None

    def addItem(self):
        if self.searchLineEdit.text() != '' and int(self.quantSpinbox.text()) > 0 :
            self.cur.execute("SELECT PRODID FROM products WHERE DESC LIKE '" + str(self.searchLineEdit.text())+"'")
            itemID = self.cur.fetchone()[0]
            self.data.extend([[int(self.quantSpinbox.text()), itemID, self.doubleSpinBox.text().replace(",", ".")]])
            self.insertItemsTable()
            self.doubleSpinBox.setValue(0.00)
            self.quantSpinbox.setValue(1)
            self.searchLineEdit.clear()

    def deleteItem(self):
        index = (self.tableWidget.selectionModel().currentIndex())
        if index.row() != -1:
            self.data.pop(index.row())
            self.insertItemsTable()
            self.tableWidget.clearSelection()

    def setCompleter(self):
        stringtosearch = self.searchLineEdit.text()
        sqlstr = "SELECT " \
                 "PRODID," \
                 "BARCODE," \
                 "PRICE," \
                 "QTD," \
                 "DESC " \
                 "FROM products " \
                 "WHERE BARCODE LIKE '" + stringtosearch + \
                 "%' OR DESC LIKE " + "'%" + stringtosearch + "%'"
        self.queryModel = QSqlQueryModel()
        self.compmodel = QSqlQueryModel()
        self.compmodel.setQuery(sqlstr)
        self.queryModel.setQuery(sqlstr)

        compsearch = "SELECT DESC FROM products WHERE DESC LIKE '" + stringtosearch + "%'"
        completer = QCompleter()
        self.compmodel.setQuery(compsearch)

        completer.setModel(self.compmodel)
        completer.setCompletionMode(completer.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.searchLineEdit.setCompleter(completer)

    def setCustomerCompleter(self):
        nameToSearch = self.customerLineEdit.text()

        compsearch = "SELECT NAME FROM customers WHERE NAME LIKE '" + nameToSearch + "%'"
        completer = QCompleter()
        self.customerCompModel = QSqlQueryModel()

        self.customerCompModel.setQuery(compsearch)

        completer.setModel(self.customerCompModel)
        completer.setCompletionMode(completer.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.customerLineEdit.setCompleter(completer)


    def finishSale(self,finished=1):
        areYouSure = QMessageBox()
        areYouSure.setIcon(QMessageBox.Question)
        areYouSure.setText("Are you sure you want to finish this sale?")
        areYouSure.setInformativeText("Finished sales cannot be edited anymore.")
        areYouSure.setWindowTitle("Are you sure?")
        areYouSure.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        returnValue = areYouSure.exec_()
        if returnValue == QMessageBox.Yes:
            for item in self.data:
                print(item)
                self.cur.execute("UPDATE products SET QTD = QTD - ? WHERE PRODID = ?", (item[0], item[1]))
            self.conn.commit()
            self.insertIntoDb(finished)

    def insertIntoDb(self, mode):
        exstr='INSERT INTO sales (CUSTOMID,SALEPRODS,SALETOTAL,FINISHED) VALUES(' + str(self.customId) +',"'+ str(self.data) +'",'+str(self.itemsSum)+ ','+str(mode)+');'
        print(exstr)
        self.cur.execute(exstr)
        self.conn.commit()
        self.close()


# app = QtWidgets.QApplication(sys.argv)
# window = Ui_newSaleWin()
# app.exec_()