from PyQt5.QtWidgets import (QApplication, QDialog,
                             QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit,QPushButton, QSpinBox, QTextEdit,
                             QVBoxLayout)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class addOrEdit(QDialog):
    def __init__(self, parent, mode):
        self.parent = parent
        super(addOrEdit, self).__init__()
        self.layout = QFormLayout()
        self.resize(400, 200)

        self.desc = QLineEdit()
        if mode == 'edit':
            self.formGroupBox = QGroupBox("Edit item")
            self.setWindowTitle("Edit")
        else:
            self.formGroupBox = QGroupBox("Add item")
            self.quant = QSpinBox()
            self.layout.addRow(QLabel("Quantity:"), self.quant)
            self.setWindowTitle("Add Item")

        self.cod = QLineEdit()
        self.price = QLineEdit()

        self.price.setValidator(QDoubleValidator(0.01,9999999.99,2))

        self.layout.addRow(QLabel("Description:"), self.desc)
        self.layout.addRow(QLabel("Price:"), self.price)
        self.layout.addRow(QLabel("Bar code:"), self.cod)

        self.formGroupBox.setLayout(self.layout)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.outstatus=False
        self.buttonBox.rejected.connect(lambda: self.close())

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.formGroupBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)
        self.buttonBox.accepted.connect(self.acceptedw)

    def prefset(self,prefdesc,prefcod,prefprice):
        self.desc.setText(prefdesc)
        self.cod.setText(prefcod)
        self.price.setText(str(prefprice))

    def acceptedw(self):
        self.outstatus=True
        self.close()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    dialog = addOrEdit()
    sys.exit(dialog.exec_())
