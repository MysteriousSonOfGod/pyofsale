
from PyQt5.QtGui import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtCore import *
# from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import *
import sqlite3
from decimal import Decimal as D

class Ui_newSaleWin(object):
    def setupUi(self, newSaleWin):
        newSaleWin.setObjectName("newSaleWin")
        newSaleWin.setWindowModality(QtCore.Qt.ApplicationModal)
        newSaleWin.resize(800, 470)

        self.data = []

        self.finButton = QtWidgets.QPushButton(newSaleWin)
        self.finButton.setGeometry(QtCore.QRect(710, 440, 80, 25))
        icon = QtGui.QIcon.fromTheme("checkbox")
        self.finButton.setIcon(icon)
        self.finButton.setAutoDefault(False)
        self.finButton.setDefault(False)
        self.finButton.setFlat(False)
        self.finButton.setObjectName("finButton")
        self.finButton.clicked.connect(self.finishSale)

        self.setUpConnect()

        self.saveButton = QtWidgets.QPushButton(newSaleWin)
        self.saveButton.setGeometry(QtCore.QRect(620, 440, 80, 25))
        icon = QtGui.QIcon.fromTheme("document-save")
        self.saveButton.setIcon(icon)
        self.saveButton.setObjectName("saveButton")

        self.cancelButton = QtWidgets.QPushButton(newSaleWin)
        self.cancelButton.setGeometry(QtCore.QRect(530, 440, 80, 25))
        icon = QtGui.QIcon.fromTheme("edit-delete")
        self.cancelButton.setIcon(icon)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.clicked.connect(lambda: sys.exit(0))

        self.searchLineEdit = QtWidgets.QLineEdit(newSaleWin)
        self.searchLineEdit.setGeometry(QtCore.QRect(20, 50, 341, 25))
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.searchLineEdit.returnPressed.connect(self.setPrice)
        self.searchLineEdit.editingFinished.connect(self.setPrice)

        self.quantspinbox = QtWidgets.QSpinBox(newSaleWin)
        self.quantspinbox.setGeometry(QtCore.QRect(370, 50, 121, 26))
        self.quantspinbox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.quantspinbox.setAutoFillBackground(False)
        self.quantspinbox.setKeyboardTracking(False)
        self.quantspinbox.setFrame(True)
        self.quantspinbox.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.quantspinbox.setMaximum(99999999)
        self.quantspinbox.setObjectName("quantspinbox")
        self.quantspinbox.setValue(1)

        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(newSaleWin)
        self.doubleSpinBox.setGeometry(QtCore.QRect(500, 50, 151, 26))
        self.doubleSpinBox.setObjectName("doubleSpinBox")

        self.includeBtn = QtWidgets.QPushButton(newSaleWin)
        self.includeBtn.setGeometry(QtCore.QRect(660, 50, 131, 25))
        self.includeBtn.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.includeBtn.setObjectName("includeBtn")
        self.includeBtn.clicked.connect(self.addItem)
        self.includeBtn.clicked.connect(self.searchLineEdit.setFocus)

        self.deletebtn = QtWidgets.QPushButton(newSaleWin)
        self.deletebtn.setGeometry(QtCore.QRect(710, 240, 80, 70))
        self.deletebtn.setStyleSheet("background-color: rgb(239, 41, 41);")
        self.deletebtn.setObjectName("deletebtn")
        self.deletebtn.clicked.connect(self.deleteItem)

        self.searchLabel = QtWidgets.QLabel(newSaleWin)
        self.searchLabel.setGeometry(QtCore.QRect(20, 30, 241, 17))
        self.searchLabel.setObjectName("searchLabel")

        self.quantlabel = QtWidgets.QLabel(newSaleWin)
        self.quantlabel.setGeometry(QtCore.QRect(370, 30, 81, 17))
        self.quantlabel.setObjectName("quantlabel")

        self.priceLabel = QtWidgets.QLabel(newSaleWin)
        self.priceLabel.setGeometry(QtCore.QRect(500, 30, 71, 17))
        self.priceLabel.setObjectName("priceLabel")

        self.label = QtWidgets.QLabel(newSaleWin)
        self.label.setGeometry(QtCore.QRect(310, 430, 150, 21))
        self.label.setObjectName("label")

        self.tableWidget = QtWidgets.QTableWidget(newSaleWin)
        self.tableWidget.setGeometry(QtCore.QRect(20, 90, 681, 321))
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.alphaOrderCheck = QtWidgets.QCheckBox(newSaleWin)
        self.alphaOrderCheck.setGeometry(QtCore.QRect(20, 420, 131, 23))
        self.alphaOrderCheck.setObjectName("alphaOrderCheck")

        self.quantspinbox.valueChanged.connect(lambda: self.doubleSpinBox.setFocus())

        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.insertItemsTable()
        self.setCompleter()

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
            self.searchLineEdit.returnPressed.connect(lambda: self.quantspinbox.setFocus())

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
            self.label.setText("Total: "+str(self.itemsSum))

        self.tableWidget.clearSelection()
        self.retranslateUi(newSaleWin)
        QtCore.QMetaObject.connectSlotsByName(newSaleWin)
        if self.alphaOrderCheck.isChecked():
            self.tableWidget.sortByColumn(1, Qt.AscendingOrder)

    def addItem(self):
        if self.searchLineEdit.text() != '' and int(self.quantspinbox.text()) > 0 :
            self.cur.execute("SELECT PRODID FROM products WHERE DESC LIKE '" + str(self.searchLineEdit.text()) + "%'")
            itemID = self.cur.fetchone()[0]
            self.data.extend([[int(self.quantspinbox.text()), itemID, self.doubleSpinBox.text().replace(",", ".")]])
            self.insertItemsTable()
            self.doubleSpinBox.setValue(0.00)
            self.quantspinbox.setValue(1)
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

    def finishSale(self):
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
            self.insertIntoDb(1)


    def insertIntoDb(self, mode):
        self.cur.execute('INSERT INTO sale (SALEPRODS,SALETOTAL,FINISHED) VALUES("' + str(self.data) +'",' +str(self.itemsSum)+ ','+str(mode)+');')
        self.conn.commit()
        sys.exit(0)


    def retranslateUi(self, newSaleWin):
        _translate = QtCore.QCoreApplication.translate
        newSaleWin.setWindowTitle(_translate("newSaleWin", "newSaleWin"))
        self.deletebtn.setText(_translate("newSaleWin", "Delete"))
        self.includeBtn.setText(_translate("newSaleWin", "Include"))
        self.searchLabel.setText(_translate("newSaleWin", "Search for description or barcode:"))
        self.quantlabel.setText(_translate("newSaleWin", "Quantity:"))
        self.priceLabel.setText(_translate("newSaleWin", "Price:"))
        self.finButton.setText(_translate("newSaleWin", "Finish"))
        self.saveButton.setText(_translate("newSaleWin", "Save"))
        self.cancelButton.setText(_translate("newSaleWin", "Cancel"))
        self.alphaOrderCheck.setText(_translate("newSaleWin", "Alphabetical Order"))

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    newSaleWin = QtWidgets.QWidget()
    ui = Ui_newSaleWin()
    ui.setupUi(newSaleWin)
    newSaleWin.show()
    sys.exit(app.exec_())
