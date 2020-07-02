from PyQt5.QtGui import *

from PyQt5 import QtCore, QtGui, QtWidgets,uic
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QCompleter, QMessageBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtCore import *

import datetime
import sqlite3
from decimal import Decimal as D

import sys

class Ui_purchOrder(QtWidgets.QMainWindow):
    def __init__(self,purchId=None):
        super(Ui_purchOrder, self).__init__()

        uic.loadUi('purchOrder/purchOrder.ui', self)
        self.data = []
        self.purchId=purchId
        self.setUpConnect()
        self.setCompleter()
        self.setSupplierCompleter()

        if self.purchId is not None:
            import ast
            self.cur.execute("SELECT PURCHID, SALEPRODS, SALETIME, FINISHED, NAME FROM purchorders, suppliers WHERE PURCHID LIKE ? ",(self.purchId,))
            sqlReturn=self.cur.fetchone()
            prodsStr=sqlReturn[1]
            self.data.extend(ast.literal_eval(prodsStr))
            self.setSupplier()
            if sqlReturn[3]==1:
                self.finButton.setEnabled(False)
                self.saveButton.setEnabled(False)
                self.includeBtn.setEnabled(False)
                self.deleteBtn.setEnabled(False)
                self.supplierLineEdit.setEnabled(False)
                self.searchLineEdit.setEnabled(False)
                self.quantSpinbox.setEnabled(False)
                self.doubleSpinBox.setEnabled(False)

        self.insertItemsTable()

        self.cancelButton.clicked.connect(lambda: self.close())
        self.includeBtn.clicked.connect(self.addItem)
        self.includeBtn.clicked.connect(self.searchLineEdit.setFocus)
        self.saveButton.clicked.connect(lambda: self.finishSale(False))
        self.supplierLineEdit.editingFinished.connect(self.setSupplier)
        self.finButton.clicked.connect(lambda: self.finishSale(True))
        self.deleteBtn.clicked.connect(self.deleteItem)

        self.searchLineEdit.editingFinished.connect(self.setCost)
        self.quantSpinbox.setKeyboardTracking(False)

        self.show()

    def setUpConnect(self):
        self.conn = sqlite3.connect('pyofsaledb.db')
        self.cur = self.conn.cursor()
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("pyofsaledb.db")
        self.db.open()

    def setCost(self):
        if self.searchLineEdit.text() != '':
            self.cur.execute("SELECT COST FROM products WHERE DESC LIKE ? ",(self.searchLineEdit.text() + "%",))
            itemCost = self.cur.fetchone()[0]
            self.doubleSpinBox.setValue(float(itemCost))
            self.searchLineEdit.returnPressed.connect(lambda: self.quantSpinbox.setFocus())

    def insertItemsTable(self):
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(3)

        self.tableWidget.setHorizontalHeaderLabels(['Quant', 'Desc', 'Cost'])

        self.tableWidget.setRowCount(len(self.data))

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


        for row in range(len(self.data)):
            self.cur.execute("SELECT DESC FROM products WHERE PRODID LIKE ?", (str(self.data[row][1]) + "%",))
            itemDesc = self.cur.fetchone()[0]

            self.tableWidget.setItem(row, 0, QTableWidgetItem(str((self.data[row][0]))))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(itemDesc)))
            self.tableWidget.setItem(row, 2, QTableWidgetItem((self.data[row][2])))


    def setSupplier(self):
        self.suppId=0
        if self.supplierLineEdit.text() is not None and self.purchId is None:
            self.cur.execute('SELECT SUPPID FROM suppliers WHERE NAME LIKE ?', (self.supplierLineEdit.text(),))

            self.suppId = self.cur.fetchone()[0]
        elif self.purchId is not None:
            self.cur.execute('SELECT NAME FROM purchorders, suppliers WHERE PURCHID LIKE ' + str(self.purchId))
            self.supplierLineEdit.setText(str(self.cur.fetchone()[0]))
            self.cur.execute('SELECT SUPPID FROM suppliers WHERE NAME LIKE ?', (self.supplierLineEdit.text(),) )
            self.suppId = self.cur.fetchone()[0]
        else:
            self.suppId=None


    def addItem(self):
        if self.searchLineEdit.text() != '' and int(self.quantSpinbox.text()) > 0 :
            self.cur.execute("SELECT PRODID FROM products WHERE DESC LIKE ?",(self.searchLineEdit.text(),))
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
                 "COST," \
                 "QTY," \
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

    def setSupplierCompleter(self):
        nameToSearch = self.supplierLineEdit.text()

        compsearch = "SELECT NAME FROM suppliers WHERE NAME LIKE '" + nameToSearch + "%'"
        completer = QCompleter()
        self.supplierCompModel = QSqlQueryModel()

        self.supplierCompModel.setQuery(compsearch)

        completer.setModel(self.supplierCompModel)
        completer.setCompletionMode(completer.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.supplierLineEdit.setCompleter(completer)


    def finishSale(self,finished=True):
        areYouSure = QMessageBox()
        areYouSure.setIcon(QMessageBox.Question)
        areYouSure.setText("Are you sure you want to finish this sale?")
        areYouSure.setInformativeText("Finished purchase orders cannot be edited anymore.")
        areYouSure.setWindowTitle("Are you sure?")
        areYouSure.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        returnValue = areYouSure.exec_()

        if returnValue == QMessageBox.Yes:
            for item in self.data:
                self.cur.execute("UPDATE products SET COST =?, QTY = QTY + ? WHERE PRODID = ?", (item[2],item[0], item[1],))
            self.conn.commit()
            self.insertIntoDb(finished)

    def insertIntoDb(self, mode):
        if self.purchId is None:
            self.cur.execute(
                "INSERT INTO purchorders (SUPPID,PURCHPRODS,PURCHTOTAL,FINISHED) VALUES (?,?,?,?)",
                (self.suppId,
                 str(self.data),
                 str(self.itemsSum),
                 mode,))

        else:
            ("UPDATE purchorders SET PURCHPRODS=?, PURCHTOTAL=?, FINISHED=?, SUPPID=?, WHERE PURCHID = ? ",
             (str(self.data),
              self.itemsSum,
              mode,
             self.purchId,))

        self.conn.commit()
        self.close()

# app = QtWidgets.QApplication(sys.argv)
# window = Ui_purchOrder()
# app.exec_()
