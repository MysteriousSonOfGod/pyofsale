from PyQt5 import QtCore, QtWidgets, uic
import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import sqlite3
import json
import ast
from modules.addOrEditDialog import addOrEdit
from modules.settswin import Ui_settingsWindow
from modules.viewSale import Ui_viewSale
from newSale.newSale import Ui_newSaleWin
from addOrEditCustomer.main import addOrEditCustomer_Ui

with open('settings.json','r') as settingsFile:
  settings = json.load(settingsFile)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('pyofsale.ui', self)

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


        self.viewSaleBtn.clicked.connect(self.showSale)
        self.newSaleBtn.clicked.connect(self.newSaleFunc)
        self.addCustomerBtn.clicked.connect(self.addCustomer)

        self.actionSettings.triggered.connect(self.openSettings)

        self.actionAbout.triggered.connect(lambda: QtWidgets.QMessageBox.about(self, "About", "Made by Nicolas Morais, with SQLite3 and PyQT5."))

        self.dbConnect()
        self.customerSearch()
        self.getMaxMinDate()
        self.searchDate()
        self.searchString()
        self.show()

    def dbConnect(self):
        self.conn = sqlite3.connect('pyofsaledb.db')
        self.cur = self.conn.cursor()

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("pyofsaledb.db")
        self.db.open()
        self.cur.execute("CREATE TABLE IF NOT EXISTS sales (SALEID INTEGER PRIMARY KEY AUTOINCREMENT, SALEPRODS TEXT, "
                         "SALETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW','LOCALTIME')),SALETOTAL TEXT,"
                         "FINISHED BOOLEAN DEFAULT '0', CUSTOMID INTEGER, FOREIGN KEY (CUSTOMID) REFERENCES "
                         "customers(CUSTOMID));")
        self.cur.execute("CREATE TABLE IF NOT EXISTS products (PRODID INTEGER PRIMARY KEY AUTOINCREMENT, BARCODE "
                         "TEXT, DESC TEXT NOT NULL UNIQUE, PRICE REAL DEFAULT '0', QTD INTEGER DEFAULT '0');")
        self.cur.execute("CREATE TABLE IF NOT EXISTS customers (CUSTOMID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT "
                         "NOT NULL UNIQUE, EMAIL TEXT, PHONE TEXT, ADDRESS TEXT);")

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
            self.salesComboBox.setEnabled(False)
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

        self.cur.execute("SELECT SUM(SALETOTAL) FROM sales WHERE SALETIME LIKE '" + str(date.toPyDate())[:-2] + "%' AND FINISHED = 1")
        monthSumDb = self.cur.fetchone()
        self.monthSumLabel.setText("Month Total: " + str(monthSumDb[0]))

    def searchString(self):
        stringtosearch = self.searchProd.text()
        sqlstr = "SELECT " \
                 "PRODID," \
                 "BARCODE," \
                 "PRICE," \
                 "QTD," \
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
        settingsWin = Ui_settingsWindow(parent='self')
        settingsWin.exec_()
        if settingsWin.newsettings:
            QtWidgets.QMessageBox.information(self, "Info",
                                    "Restart the program apply new settings.")

    def monthsum(self, yearmonthstr):
        self.cur.execute(
            "SELECT SUM(SALETOTAL) FROM sales WHERE SALETIME LIKE '" + yearmonthstr + "%' AND FINISHED = 1")
        monthSumDb = self.cur.fetchone()
        self.monthSumLabel.setText("Total no mes" + str(monthSumDb))

    def showSale(self):
        index = (self.salesTableView.selectionModel().currentIndex())
        value = index.sibling(index.row(), 0).data()
        saleList = ((self.rowprint(value, "SALEID", "sales")[1]))

        salesMatrix = ast.literal_eval(saleList)

        for item in salesMatrix:
            self.cur.execute("SELECT DESC FROM products WHERE PRODID=" + str(item[1]))
            row = self.cur.fetchone()
            item[1] = str(row[0])
        self.cur.execute("SELECT SALETIME FROM sales WHERE SALEID=" + str(value))
        tradedatehour = self.cur.fetchone()
        self.visuwindow = MainWindowt(salesMatrix, "Sale at " + str(tradedatehour[0]))

    def newSaleFunc(self):
        Ui_newSaleWin()

    def runadd(self, mode, primkey=0, descPrefill="", codPrefill="", pricePrefill=""):
        addwindow = addOrEdit(parent='self', mode=mode)
        if mode == 'edit':
            addwindow.prefset(descPrefill, codPrefill, pricePrefill)
        addwindow.exec_()
        if addwindow.outstatus:
            if mode == 'edit':
                self.cur.execute(
                    "UPDATE products SET DESC = '" + addwindow.desc.text() + "', BARCODE='" + addwindow.cod.text() +
                    "', PRICE=" + str(addwindow.price.text()) + " WHERE PRODID =" + str(primkey))
            else:
                self.cur.execute(
                    "INSERT INTO products (DESC,BARCODE,PRICE,QTD) VALUES ('" + addwindow.desc.text() + "','" + addwindow.cod.text() +
                    "'," + addwindow.price.text() + "," + addwindow.quant.text() + ")")
        self.conn.commit()
        self.db.close()
        self.dbConnect()
        self.searchString()

    def customerSearch(self):
        if self.searchCustomerMode.currentIndex() == 0:
            column = "NAME"
        elif self.searchCustomerMode.currentIndex() == 1:
            column = "PHONE"
        elif self.searchCustomerMode.currentIndex() == 2:
            column = "ADDRESS"
        else:
            column = "EMAIL"
        wildcard1 = "'"
        if self.startsOrContains.currentIndex() == 1:
            wildcard1 = "'%"
        wildcard2 = "%' LIMIT 50"

        sqlstr = "SELECT EMAIL,PHONE,ADDRESS,NAME FROM customers WHERE " + column + " LIKE " + wildcard1 + self.searchCustomer.text() + wildcard2
        self.queryModel = QSqlQueryModel()
        self.queryModel.setQuery(sqlstr)
        self.customersTableView.setModel(self.queryModel)

    def addCustomer(self):
        addOrEditCustomer_Ui()
        self.db.close()
        self.dbConnect()
        self.customerSearch()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()