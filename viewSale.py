from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog,QApplication

class Ui_viewSale(QDialog):
    def __init__(self, parent,datain):
        self.parent = parent
        super(Ui_viewSale, self).__init__()


        self.setObjectName("visualizarvendawindow")
        self.resize(613, 419)

        self.tableViewSale = QtWidgets.QTableView(self)
        self.tableViewSale.setGeometry(QtCore.QRect(20, 50, 551, 281))
        self.tableViewSale.setObjectName("tableViewSale")
        self.tableViewSale.setModel(datain)

        self.okbutton = QtWidgets.QDialogButtonBox(self)
        self.okbutton.setGeometry(QtCore.QRect(520, 380, 81, 25))
        self.okbutton.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.okbutton.setObjectName("okbutton")
        self.totalvisuvendalabel = QtWidgets.QLabel(self)
        self.totalvisuvendalabel.setGeometry(QtCore.QRect(400, 340, 54, 17))
        self.totalvisuvendalabel.setObjectName("totalvisuvendalabel")
        self.saleAtLabel = QtWidgets.QLabel(self)
        self.saleAtLabel.setGeometry(QtCore.QRect(20, 30, 311, 17))
        self.saleAtLabel.setObjectName("saleAtLabel")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("visualizarvendawindow", "visualizarvendawindow"))
        self.totalvisuvendalabel.setText(_translate("visualizarvendawindow", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">Total: </span></p></body></html>"))
        self.saleAtLabel.setText(_translate("visualizarvendawindow", "Sale at: "))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = Ui_visuwin()
    # print(desctxt)
    sys.exit(dialog.exec_())
