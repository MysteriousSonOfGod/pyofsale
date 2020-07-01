from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import QPoint
import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import sqlite3
import json
import ast
import webbrowser
from modules.addOrEditDialog import addOrEdit
from settingsWindow.main import settingsWindow
from newSale.newSale import Ui_newSaleWin
from purchOrder.main import Ui_purchOrder

from addOrEditCustomer.main import addOrEditCustomer_Ui
from addOrEditSupplier.main import addOrEditSupplier_Ui

with open('settings.json', 'r') as settingsFile:
    settings = json.load(settingsFile)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('pyofsale.ui', self)

        self.tabWidget.setTabPosition(settings["tabsPosition"])
        self.tabWidget.setTabShape(settings["tabsShape"])

        self.addbutton.clicked.connect(self.runadd)
        self.editbutton.clicked.connect(self.onclick)

        self.searchProd.textChanged.connect(self.searchString)
        self.tableView.doubleClicked['QModelIndex'].connect(self.onclick)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.salesComboBox.currentIndexChanged.connect(self.searchDate)

        self.searchCustomer.textChanged.connect(self.customerSearch)
        self.searchCustomerMode.currentIndexChanged.connect(self.customerSearch)

        self.customersTableView.horizontalHeader().setStretchLastSection(True)
        self.customersTableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.customersTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.customersTableView.clicked['QModelIndex'].connect(lambda: self.editCustomerBtn.setEnabled(True))
        self.customersTableView.doubleClicked['QModelIndex'].connect(lambda: self.addCustomer(add=False))

        self.editCustomerBtn.clicked.connect(lambda: self.addCustomer(add=False))
        self.editSupplierBtn.clicked.connect(lambda: self.addSupplier(add=False))

        self.viewSaleBtn.clicked.connect(self.showSale)
        self.newSaleBtn.clicked.connect(lambda: Ui_newSaleWin())
        self.addPurchOrder.clicked.connect(lambda: Ui_purchOrder())

        self.salesTableView.doubleClicked['QModelIndex'].connect(lambda: self.showSale())

        self.addCustomerBtn.clicked.connect(self.addCustomer)
        self.addSupplierBtn.clicked.connect(lambda: self.addSupplier())

        self.actionSettings.triggered.connect(self.openSettings)

        self.actionAbout.triggered.connect(
            lambda: QtWidgets.QMessageBox.about(self, "About", "Made by Nicolas Morais, with SQLite3 and PyQT5."))

        self.dbConnect()

        self.supplierSearch()
        self.setSupOrderMenu()
        self.searchSuppLine.textChanged.connect(self.supplierSearch)

        self.calendarWidget.clicked.connect(self.searchDate)

        self.customerSearch()
        self.getMaxMinDate()
        self.searchDate()
        self.replDateSearch()
        self.searchString()
        self.show()

    def dbConnect(self):
        self.conn = sqlite3.connect('pyofsaledb.db')
        self.cur = self.conn.cursor()

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("pyofsaledb.db")
        self.db.open()
        self.cur.execute(" CREATE TABLE IF NOT EXISTS sales (SALEID INTEGER PRIMARY KEY AUTOINCREMENT, SALEPRODS TEXT,"
                         " SALETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW','LOCALTIME')),SALETOTAL REAL,"
                         "FINISHED BOOLEAN DEFAULT '0', CUSTOMID INTEGER, FOREIGN KEY (CUSTOMID) REFERENCES customers(CUSTOMID));")

        self.cur.execute("CREATE TABLE IF NOT EXISTS products (PRODID INTEGER PRIMARY KEY AUTOINCREMENT, BARCODE TEXT,"
                         " DESC TEXT NOT NULL UNIQUE, PRICE REAL DEFAULT 0, COST REAL DEFAULT 0, QTY REAL DEFAULT 0);")

        self.cur.execute("CREATE TABLE IF NOT EXISTS customers (CUSTOMID INTEGER PRIMARY KEY AUTOINCREMENT, "
                         "NAME TEXT NOT NULL UNIQUE, EMAIL TEXT, PHONE TEXT, ADDRESS TEXT);")

        self.cur.execute("CREATE TABLE IF NOT EXISTS suppliers (SUPPID INTEGER PRIMARY KEY AUTOINCREMENT,"
                         " NAME TEXT NOT NULL UNIQUE, EMAIL TEXT, PHONE TEXT, ADDRESS TEXT);")

        self.cur.execute(" CREATE TABLE IF NOT EXISTS purchorders (PURCHID INTEGER PRIMARY KEY AUTOINCREMENT,"
                         " PURCHPRODS TEXT, PURCHTIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW','LOCALTIME')),"
                         "PURCHTOTAL REAL,FINISHED BOOLEAN DEFAULT '0', SUPPID INTEGER, "
                         "FOREIGN KEY (SUPPID) REFERENCES SUPPLIERS(SUPPID));")

    def getMaxMinDate(self):
        self.cur.execute("SELECT SALETIME FROM sales LIMIT 1;")
        minDate = self.cur.fetchone()
        if minDate is not None:
            minDate = ((minDate[0])[:10])
            self.calendarWidget.setMinimumDate(QtCore.QDate(int(minDate[:4]), int(minDate[5:7]), int(minDate[8:])))

            self.cur.execute("SELECT SALETIME FROM sales ORDER BY SALETIME DESC LIMIT 1;")
            maxDate = self.cur.fetchone()
            maxDate = ((maxDate[0])[:10])
            self.calendarWidget.setMaximumDate(QtCore.QDate(int(maxDate[:4]), int(maxDate[5:7]), int(maxDate[8:])))
        else:
            self.calendarWidget.setEnabled(False)
            self.viewSaleBtn.setEnabled(False)

    def rowprint(self, primarikeycolumn, primaykey, table):
        self.cur.execute("SELECT * FROM " + table + " WHERE " + str(primarikeycolumn) + " =" + str(primaykey))
        row = self.cur.fetchone()
        return row

    def onclick(self):
        index = (self.tableView.selectionModel().currentIndex())
        value = index.sibling(index.row(), 0).data()
        rowtuple = self.rowprint(value, "PRODID", "products")
        self.runadd('edit', rowtuple[0], rowtuple[2], rowtuple[1], rowtuple[3])

    def searchDate(self):
        date = self.calendarWidget.selectedDate()
        sqlstrdate = "SELECT SALEID, SALETIME, SALETOTAL, FINISHED,NAME FROM sales,customers WHERE " \
                     "sales.CUSTOMID=customers.CUSTOMID AND SALETIME LIKE '" + str(
            date.toPyDate()) + "%'"

        if self.salesComboBox.currentIndex() == 1:
            sqlstrdate += " AND FINISHED = 1"
        self.queryModel = QSqlQueryModel()

        self.queryModel.setQuery(sqlstrdate)

        self.salesTableView.setModel(self.queryModel)

        self.cur.execute("SELECT SUM(SALETOTAL) FROM sales WHERE SALETIME LIKE ? ",
                         ((str(date.toPyDate())[:-2]) + '%',))
        monthSumDb = self.cur.fetchone()
        self.monthSumLabel.setText("Month Total: " + str(monthSumDb[0]))

    def replDateSearch(self):
        replDate = self.replCalendar.selectedDate()
        self.queryModel = QSqlQueryModel()
        replSqrStr="SELECT PURCHID, PURCHTIME, PURCHTOTAL, FINISHED,NAME FROM purchorders,suppliers WHERE " \
                     "purchorders.SUPPID=suppliers.SUPPID AND PURCHTIME LIKE '" + str(
            replDate.toPyDate()) + "%'"

        self.queryModel.setQuery(replSqrStr)

        self.replTableView.setModel(self.queryModel)

        # self.cur.execute("SELECT SUM(PURCHTOTAL) FROM purchorders WHERE PURCHTIME LIKE ? ",
        #                  ((str(replDate.toPyDate())[:-2]) + '%',))

    def searchString(self):
        stringtosearch = self.searchProd.text()
        sqlstr = "SELECT " \
                 "PRODID," \
                 "BARCODE," \
                 "PRICE," \
                 "QTY," \
                 "DESC " \
                 "FROM products " \
                 "WHERE BARCODE LIKE '" + stringtosearch + \
                 "%' OR DESC LIKE " + "'" + stringtosearch + "%'"

        self.queryModel = QSqlQueryModel()
        self.queryModel.setQuery(sqlstr)
        self.tableView.setModel(self.queryModel)
        if not settings["showVerticalHeader"]:
            self.tableView.verticalHeader().setVisible(False)

    def openSettings(self):
        settsWindow = settingsWindow()
        settsWindow.exec_()

    def monthsum(self, yearmonthstr):
        self.cur.execute("SELECT SUM(SALETOTAL) FROM sales WHERE SALETIME LIKE ? AND FINISHED =1 ",
                         (yearmonthstr + "%'"),)
        monthSumDb = self.cur.fetchone()
        self.monthSumLabel.setText("Total no mes" + str(monthSumDb))

    def showSale(self):
        index = (self.salesTableView.selectionModel().currentIndex())
        value = index.sibling(index.row(), 0).data()
        Ui_newSaleWin(saleId=str(value))

    def runadd(self, mode, primkey=0, descPrefill="", codPrefill="", pricePrefill=""):
        addwindow = addOrEdit(parent='self', mode=mode)
        if mode == 'edit':
            addwindow.prefset(descPrefill, codPrefill, pricePrefill)
        addwindow.exec_()
        if addwindow.outstatus:
            if mode == 'edit':
                self.cur.execute(
                    "UPDATE products SET DESC=?, BARCODE=?, PRICE=?, WHERE PRODID=?",
                    (addwindow.desc.text(),
                     addwindow.cod.text(),
                     addwindow.price.text(),
                     primkey,))
            else:
                self.cur.execute(
                    "INSERT INTO products (DESC,BARCODE,PRICE,QTY) VALUES (?,?,?,?) ",
                    (addwindow.desc.text(),
                     addwindow.cod.text(),
                     addwindow.price.text(),
                     addwindow.quant.text(),))

        self.conn.commit()
        self.db.close()
        self.dbConnect()
        self.searchString()

    def setSupOrderMenu(self):

        self.SupOrderMenu = QtWidgets.QMenu()
        self.emailSupAction = self.SupOrderMenu.addAction('E-mail Supplier')

    def customerSearch(self):
        if self.searchCustomerMode.currentIndex() == 0:
            column = "NAME"
        elif self.searchCustomerMode.currentIndex() == 1:
            column = "PHONE"
        elif self.searchCustomerMode.currentIndex() == 2:
            column = "ADDRESS"
        else:
            column = "EMAIL"
        wildcard = "'"
        if self.startsOrContains.currentIndex():
            wildcard = "'%"

        sqlstr = "SELECT CUSTOMID, EMAIL, PHONE, ADDRESS, NAME FROM customers WHERE " + column + " LIKE " + wildcard + self.searchCustomer.text() + "%' LIMIT 50"
        self.queryModel = QSqlQueryModel()
        self.queryModel.setQuery(sqlstr)
        self.customersTableView.setModel(self.queryModel)
        self.customersTableView.setColumnHidden(0, True)
        if not settings["showVerticalHeader"]:
            self.customersTableView.verticalHeader().setVisible(False)
    def addCustomer(self, add=True):
        index = (self.customersTableView.selectionModel().currentIndex())
        value = index.sibling(index.row(), 0).data()

        if add:
            addOrEditCustomer_Ui()
        else:
            addOrEditCustomer_Ui(value)
        self.db.close()
        self.dbConnect()

        self.editCustomerBtn.setEnabled(False)
        self.customerSearch()

    def supplierSearch(self):
        self.queryModel = QSqlQueryModel()
        self.queryModel.setQuery("SELECT SUPPID,EMAIL,PHONE,ADDRESS,NAME FROM suppliers WHERE NAME LIKE '" + self.searchSuppLine.text() + "%'")
        self.suppliersTableView.setModel(self.queryModel)
        self.suppliersTableView.horizontalHeader().setStretchLastSection(True)
        self.suppliersTableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.suppliersTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.suppliersTableView.clicked['QModelIndex'].connect(lambda: self.editSupplierBtn.setEnabled(True))
        self.suppliersTableView.clicked['QModelIndex'].connect(lambda: self.orderBtn.setEnabled(True))
        self.suppliersTableView.clicked['QModelIndex'].connect(lambda: self.orderToolButton.setEnabled(True))
        self.suppliersTableView.doubleClicked['QModelIndex'].connect(lambda: self.addSupplier(add=False))
        self.orderToolButton.clicked.connect(lambda: self.SupOrderMenu.exec_(self.orderToolButton.mapToGlobal(QPoint(0, 20))))
        self.suppliersTableView.setColumnHidden(0, True)
        self.editSupplierBtn.setEnabled(False)

        if not settings["showVerticalHeader"]:
            self.suppliersTableView.verticalHeader().setVisible(False)

    def addSupplier(self, add=True):
        if add:
            addOrEditSupplier_Ui()
        else:
            index = (self.suppliersTableView.selectionModel().currentIndex())
            value = index.sibling(index.row(), 0).data()
            addOrEditSupplier_Ui(value)

        self.customerSearch()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
