from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtWidgets import QDialog
import json

with open('settings.json') as jsonconfigs:
    configsfile = json.load(jsonconfigs)

class settingsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(settingsWindow, self).__init__()
        uic.loadUi('settingsWindow/form.ui', self)

        if configsfile['showVerticalHeader']:
            self.yesRadioBtn.setChecked(True)
        else:
            self.noRadioBtn.setChecked(True)

        self.tabsPosCombo.setCurrentIndex(configsfile['tabsPosition'])
        self.tabsShapeCombo.setCurrentIndex(configsfile['tabsShape'])
        self.buttonBox.accepted.connect(self.setconfigs)
        self.show()
    def setconfigs(self):

        settings={'showVerticalHeader':self.yesRadioBtn.isChecked(),
                  'tabsPosition':self.tabsPosCombo.currentIndex(),
                  'tabsShape':self.tabsShapeCombo.currentIndex()}

        with open('settings.json', 'w') as configsfile:
            json.dump(settings, configsfile)
        QtWidgets.QMessageBox.information(self, "Info",
                                          "Restart the program apply new settings.")

        self.close()

# app = QtWidgets.QApplication(sys.argv)
# window = settingsWindow()
# app.exec_()
