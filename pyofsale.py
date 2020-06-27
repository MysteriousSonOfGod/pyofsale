import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import *

from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from modules.addOrEditDialog import addOrEdit

from modules.settswin import Ui_settingsWindow
from modules.viewSale import Ui_viewSale
from modules.newSale import Ui_newSaleWin

import ast
import json


with open('settings.json') as jsonconfigs:
    configsfile = json.load(jsonconfigs)


class Ui_mainwindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_mainwindow, self).__init__(parent=parent)

        self.setupUi(self)

    def setupUi(self, mainwindow):
        mainwindow.setObjectName("mainwindow")
        mainwindow.resize(800, 600)
        mainwindow.setMinimumSize(QtCore.QSize(300, 300))
        mainwindow.setWindowTitle("PyOfSale")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.jpeg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        mainwindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")

        self.dbConnect()

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 10, 750, 530))
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.tabBarClicked.connect(self.customerSearch)

        self.productsTab = QtWidgets.QWidget()
        self.productsTab.setObjectName("productsTab")

        self.tableView = QtWidgets.QTableView(self.productsTab)
        self.tableView.setGeometry(QtCore.QRect(20, 70, 610, 390))
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.doubleClicked['QModelIndex'].connect(self.onclick)

        self.lineEdit = QtWidgets.QLineEdit(self.productsTab)
        self.lineEdit.setGeometry(QtCore.QRect(20, 30, 610, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.returnPressed.connect(self.searchString)
        self.lineEdit.textChanged.connect(self.searchString)

        self.addbutton = QtWidgets.QPushButton(self.productsTab)
        self.addbutton.setGeometry(QtCore.QRect(650, 390, 80, 71))
        self.addbutton.setObjectName("addbutton")
        addicon = QtGui.QIcon.fromTheme("list-add")
        self.addbutton.setIcon(addicon)
        self.addbutton.setIconSize(QtCore.QSize(16, 16))
        self.addbutton.clicked.connect(self.runadd)

        self.editbutton = QtWidgets.QPushButton(self.productsTab)
        self.editbutton.setGeometry(QtCore.QRect(650, 300, 80, 71))
        self.editbutton.setObjectName("editbutton")
        self.editbutton.clicked.connect(self.onclick)

        self.tabWidget.addTab(self.productsTab, "")
        self.sellTab = QtWidgets.QWidget()
        self.sellTab.setObjectName("sellTab")

        self.tabWidget.addTab(self.sellTab, "")
        mainwindow.setCentralWidget(self.centralwidget)

        self.monthSumLabel = QtWidgets.QLabel(self.sellTab)
        self.monthSumLabel.setGeometry(QtCore.QRect(350, 160, 150, 17))
        self.monthSumLabel.setObjectName("monthSumLabel")

        self.calendarWidget = QtWidgets.QCalendarWidget(self.sellTab)
        self.calendarWidget.setGeometry(QtCore.QRect(20, 10, 310, 171))
        self.calendarWidget.setGridVisible(True)
        self.calendarWidget.setHorizontalHeaderFormat(QtWidgets.QCalendarWidget.ShortDayNames)
        self.calendarWidget.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.calendarWidget.setNavigationBarVisible(True)
        self.calendarWidget.setDateEditEnabled(True)
        self.calendarWidget.setObjectName("calendarWidget")
        self.calendarWidget.clicked[QtCore.QDate].connect(self.searchDate)

        self.menubar = QtWidgets.QMenuBar(mainwindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")

        self.salesTableView = QtWidgets.QTableView(self.sellTab)
        self.salesTableView.setGeometry(QtCore.QRect(20, 200, 611, 261))
        self.salesTableView.setObjectName("salesTableView")
        self.salesTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.salesTableView.setSortingEnabled(True)

        self.salesTableView.doubleClicked['QModelIndex'].connect(self.showSale)

        self.salesComboBox = QtWidgets.QComboBox(self.sellTab)
        self.salesComboBox.setGeometry(QtCore.QRect(610, 30, 121, 25))
        self.salesComboBox.setObjectName("salesComboBox")
        self.salesComboBox.addItem("All")
        self.salesComboBox.addItem("Finished Only")
        self.salesComboBox.currentIndexChanged.connect(self.searchDate)

        if configsfile["showVerticalHeader"]:
            self.salesTableView.verticalHeader().setVisible(True)
        else:
            self.salesTableView.verticalHeader().setVisible(False)

        self.newSaleBtn = QtWidgets.QPushButton(self.sellTab)
        self.newSaleBtn.setGeometry(QtCore.QRect(650, 390, 81, 71))
        self.newSaleBtn.setObjectName("newSaleBtn")

        self.viewBtn = QtWidgets.QPushButton(self.sellTab)
        self.viewBtn.setGeometry(QtCore.QRect(650, 300, 80, 71))
        self.viewBtn.setObjectName("viewBtn")
        self.viewBtn.clicked.connect(self.showSale)

        self.customersTab = QtWidgets.QWidget()
        self.customersTab.setEnabled(True)
        self.customersTab.setAccessibleName("")
        self.customersTab.setObjectName("customersTab")

        self.customersTableView = QtWidgets.QTableView(self.customersTab)
        self.customersTableView.setGeometry(QtCore.QRect(20, 70, 611, 391))
        self.customersTableView.setObjectName("customersTableView")
        self.customersTableView.horizontalHeader().setStretchLastSection(True)
        self.customersTableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.customersTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        if configsfile["showVerticalHeader"]:
            self.tableView.verticalHeader().setVisible(True)
            self.customersTableView.verticalHeader().setVisible(True)
        else:
            self.tableView.verticalHeader().setVisible(False)
            self.customersTableView.verticalHeader().setVisible(False)

        self.searchCustomer = QtWidgets.QLineEdit(self.customersTab)
        self.searchCustomer.setGeometry(QtCore.QRect(20, 30, 611, 25))
        self.searchCustomer.setObjectName("searchCustomer")
        self.searchCustomer.returnPressed.connect(self.customerSearch)
        self.searchCustomer.textChanged.connect(self.customerSearch)

        self.searchCustomerMode = QtWidgets.QComboBox(self.customersTab)
        self.searchCustomerMode.setGeometry(QtCore.QRect(640, 30, 91, 25))
        self.searchCustomerMode.setObjectName("comboBox")
        self.searchCustomerMode.addItem("Name")
        self.searchCustomerMode.addItem("Phone")
        self.searchCustomerMode.addItem("Address")
        self.searchCustomerMode.addItem("E-mail")
        self.searchCustomerMode.currentIndexChanged.connect(self.customerSearch)

        self.startsOrContains = QtWidgets.QComboBox(self.customersTab)
        self.startsOrContains.setGeometry(QtCore.QRect(640, 70, 91, 25))
        self.startsOrContains.setObjectName("comboBox_2")
        self.startsOrContains.addItem("Starts with")
        self.startsOrContains.addItem("Contains")
        self.startsOrContains.currentIndexChanged.connect(self.customerSearch)

        self.clearBtn = QtWidgets.QPushButton(self.customersTab)
        self.clearBtn.setGeometry(QtCore.QRect(608, 30, 21, 25))
        self.clearBtn.setText("")
        icon = QtGui.QIcon.fromTheme("edit-clear")
        self.clearBtn.setIcon(icon)
        self.clearBtn.setFlat(True)
        self.clearBtn.setObjectName("clearBtn")
        self.clearBtn.clicked.connect(self.searchCustomer.clear)

        self.addCustomerBtn = QtWidgets.QPushButton(self.customersTab)
        self.addCustomerBtn.setGeometry(QtCore.QRect(650, 390, 80, 71))
        self.addCustomerBtn.setObjectName("addCustomerBtn")

        self.editCustomerBtn = QtWidgets.QPushButton(self.customersTab)
        self.editCustomerBtn.setGeometry(QtCore.QRect(650, 300, 80, 71))
        self.editCustomerBtn.setObjectName("editCustomerBtn")

        self.tabWidget.addTab(self.customersTab, "Customers")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.aboutMenu = QtWidgets.QMenu(self.menubar)
        self.aboutMenu.setObjectName("aboutMenu")

        mainwindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(mainwindow)
        self.statusbar.setObjectName("statusbar")

        mainwindow.setStatusBar(self.statusbar)
        self.actionSettings = QtWidgets.QAction(mainwindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/wrench.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.actionSettings.setIcon(icon1)
        self.actionSettings.setObjectName("actionSettings")
        self.actionAbout = QtWidgets.QAction(mainwindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionExit = QtWidgets.QAction(mainwindow)
        self.actionExit.setObjectName("actionExit")

        self.getMaxMinDate()

        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addAction(self.actionExit)
        self.aboutMenu.addAction(self.actionAbout)
        self.aboutMenu.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.aboutMenu.menuAction())

        self.actionExit.triggered.connect(self.closeFunction)
        self.actionSettings.triggered.connect(self.openconfigs)
        self.actionAbout.triggered.connect(self.aboutFunction)

        self.retranslateUi(mainwindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)

        self.searchString()

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
            print("min", minDate)
            minDate = ((minDate[0])[:10])
            self.calendarWidget.setMinimumDate(QtCore.QDate(int(minDate[:4]), int(minDate[5:7]), int(minDate[8:])))

            self.cur.execute("SELECT SALETIME FROM sales ORDER BY SALETIME DESC LIMIT 1;")
            maxDate = self.cur.fetchone()
            print("max", maxDate)
            maxDate = ((maxDate[0])[:10])
            self.calendarWidget.setMaximumDate(QtCore.QDate(int(maxDate[:4]), int(maxDate[5:7]), int(maxDate[8:])))
        else:
            self.calendarWidget.setEnabled(False)
            self.salesComboBox.setEnabled(False)
            self.viewBtn.setEnabled(False)

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

        if self.currentIndex() == 1:
            sqlstrdate += " AND FINISHED = 1"
        self.queryModel = QSqlQueryModel()

        self.queryModel.setQuery(sqlstrdate)

        self.salesTableView.setModel(self.queryModel)

        self.cur.execute("SELECT SUM(SALETOTAL) FROM sales WHERE SALETIME LIKE '" + str(date.toPyDate())[:-2] + "%'")
        monthSumDb = self.cur.fetchone()
        self.monthSumLabel.setText("Month Total: " + str(monthSumDb[0]))

    def searchString(self):
        stringtosearch = self.lineEdit.text()
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

    def aboutFunction(self):
        QMessageBox.about(self, "About", "Made by Nicolas Morais, with SQLite3 and PyQT5.")

    def closeFunction(self):
        self.close()

    def openconfigs(self):
        settingsWin = Ui_settingsWindow(parent='self')
        settingsWin.exec_()
        if settingsWin.newsettings:
            QMessageBox.information(self, "Info",
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
        wildcard2 = "%'"

        sqlstr = "SELECT EMAIL,PHONE,ADDRESS,NAME FROM customers WHERE " + column + " LIKE " + wildcard1 + self.searchCustomer.text() + wildcard2

        self.queryModel = QSqlQueryModel()
        self.queryModel.setQuery(sqlstr)
        self.customersTableView.setModel(self.queryModel)

    def retranslateUi(self, mainwindow):
        _translate = QtCore.QCoreApplication.translate
        self.addbutton.setText(_translate("mainwindow", "Add"))
        self.editbutton.setText(_translate("mainwindow", "Edit"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.productsTab), _translate("mainwindow", "Products"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sellTab), _translate("mainwindow", "Sell"))
        self.newSaleBtn.setText(_translate("MainWindow", "Sell"))
        self.menuFile.setTitle(_translate("mainwindow", "File"))
        self.aboutMenu.setTitle(_translate("mainwindow", "About"))
        self.actionSettings.setText(_translate("mainwindow", "Settings"))
        self.actionAbout.setText(_translate("mainwindow", "About"))
        self.actionExit.setText(_translate("mainwindow", "Exit"))
        self.viewBtn.setText(_translate("MainWindow", "View"))
        self.editCustomerBtn.setText(_translate("MainWindow", "Edit"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.customersTab), _translate("MainWindow", "Customers"))


import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = Ui_mainwindow()
    # w = QtWidgets.QMainWindow()
    # ex.setupUi(w)
    ex.show()
    # mainwindow = QtWidgets.QMainWindow()
    # ui = Ui_mainwindow()
    # ui.setupUi(mainwindow)
    # mainwindow.show()
    sys.exit(app.exec_())
