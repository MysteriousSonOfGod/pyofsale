from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
                             QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
                             QVBoxLayout)
from PyQt5 import QtCore, QtGui, QtWidgets
import json

with open('settings.json') as jsonconfigs:
    configsfile = json.load(jsonconfigs)


class Ui_settingsWindow(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(Ui_settingsWindow, self).__init__()
    # def setupUi(self, configswindow):
        self.setObjectName("configswindow")
        self.resize(380, 254)
        self.limpargroupbox = QtWidgets.QGroupBox(self)
        self.limpargroupbox.setGeometry(QtCore.QRect(20, 30, 321, 61))
        self.limpargroupbox.setObjectName("limpargroupbox")
        self.yesRadionBtn = QtWidgets.QRadioButton(self.limpargroupbox)
        self.yesRadionBtn.setGeometry(QtCore.QRect(10, 30, 101, 23))

        self.yesRadionBtn.setObjectName("yesRadionBtn")
        self.noRadioBtn = QtWidgets.QRadioButton(self.limpargroupbox)
        self.noRadioBtn.setGeometry(QtCore.QRect(70, 30, 96, 23))
        self.noRadioBtn.setObjectName("noRadioBtn")
        print("configs win print ",configsfile)

        if configsfile['showVerticalHeader']:
            self.yesRadionBtn.setChecked(True)
        else:
            self.noRadioBtn.setChecked(True)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(200, 220, 166, 25))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.setconfigs)
        self.buttonBox.rejected.connect(lambda: self.close())

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.newsettings=False
    def setconfigs(self):
        data={}
        if self.yesRadionBtn.isChecked():
            data={'showVerticalHeader':True}
        else:
            data={'showVerticalHeader': False}
        print(data)
        with open('settings.json', 'w') as configsfile:
            json.dump(data, configsfile)
        self.newsettings=True
            # QMessageBox.information(self, "Info", "bacana so reinicia o programa para aplicar essas configuracao.")

        self.close()

    def retranslateUi(self, configswindow):
        _translate = QtCore.QCoreApplication.translate
        configswindow.setWindowTitle(_translate("configswindow", "Settings"))
        self.limpargroupbox.setTitle(_translate("configswindow", "Show Vertical Header on Table View:"))
        self.yesRadionBtn.setText(_translate("configswindow", "Yes"))
        self.noRadioBtn.setText(_translate("configswindow", "No"))

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     configswindow = QtWidgets.QDialog()
#     ui = Ui_configswindow()
#     ui.setupUi(configswindow)
#     configswindow.show()
#     sys.exit(app.exec_())
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = Ui_configswindow()
    # print(desctxt)
    sys.exit(dialog.exec_())
