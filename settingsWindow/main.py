from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtWidgets import QDialog,QFileDialog
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class settingsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(settingsWindow, self).__init__()
        uic.loadUi('settingsWindow/form.ui', self)

        with open('settings.json') as jsonconfigs:
            configsfile = json.load(jsonconfigs)


        if configsfile['showVerticalHeader']:
            self.yesRadioBtn.setChecked(True)
        else:
            self.noRadioBtn.setChecked(True)

        self.tabsPosCombo.setCurrentIndex(configsfile['tabsPosition'])
        self.tabsShapeCombo.setCurrentIndex(configsfile['tabsShape'])

        self.nameLineEdit.setText(configsfile['businessName'])
        self.phoneLineEdit.setText(configsfile['businessPhone'])
        self.emailLineEdit.setText(configsfile['businessEmail'])
        self.addressLineEdit.setText(configsfile['businessAddress'])

        self.saveBtn.clicked.connect(self.writeSettings)
        self.cancelBtn.clicked.connect(lambda: self.close())
        self.browseBtn.clicked.connect(self.setLogo)
        self.logoPath=configsfile['logoPath']

        if configsfile['logoPath'] == '':
            self.businessLogo.setText("No Logo Set.")
        else:
            pixmap = QPixmap(configsfile['logoPath'])
            self.businessLogo.setPixmap(pixmap)


        self.show()

    def setLogo(self):
        self.logoPath = QFileDialog.getOpenFileName(self,("Open Image"), "", ("Image Files (*.png *.jpg *.bmp *.svg *.jpeg)"))
        self.logoPath = self.logoPath[0]
        if self.logoPath != '':
            pixmap = QPixmap(self.logoPath)
            self.businessLogo.setPixmap(pixmap)

    def writeSettings(self):
        settings={'showVerticalHeader': self.yesRadioBtn.isChecked(),
                    'tabsPosition': self.tabsPosCombo.currentIndex(),
                    'tabsShape': self.tabsShapeCombo.currentIndex(),
                    'businessName': self.nameLineEdit.text(),
                    'businessPhone': self.phoneLineEdit.text(),
                    'businessEmail': self.emailLineEdit.text(),
                    'businessAddress': self.addressLineEdit.text(),
                    'logoPath': self.logoPath
                  }
        try:
            with open('settings.json', 'w') as configsfile:
                json.dump(settings, configsfile)
        except:
            QtWidgets.QMessageBox.warning(self, "Error",
                                              "Couldn't write the new settings.")
        else:
            QtWidgets.QMessageBox.information(self, "Info",
                                              "Restart the program apply new settings.")
        finally:
            self.close()
# app = QtWidgets.QApplication(sys.argv)
# window = settingsWindow()
# app.exec_()
