# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'infoUI.ui'
#
# Created: Thu Jan 29 11:42:40 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Info(object):
    def setupUi(self, Info):
        Info.setObjectName(_fromUtf8("Info"))
        Info.resize(893, 359)
        self.verticalLayout = QtGui.QVBoxLayout(Info)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Info)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.understood = QtGui.QCheckBox(Info)
        self.understood.setObjectName(_fromUtf8("understood"))
        self.verticalLayout.addWidget(self.understood)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ok = QtGui.QPushButton(Info)
        self.ok.setEnabled(False)
        self.ok.setObjectName(_fromUtf8("ok"))
        self.horizontalLayout.addWidget(self.ok)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Info)
        QtCore.QMetaObject.connectSlotsByName(Info)

    def retranslateUi(self, Info):
        Info.setWindowTitle(_translate("Info", "Info", None))
        self.label.setText(_translate("Info", "Please note:\n"
"\n"
"If you have a problem read \"Help\" first!\n"
"\n"
"-Read Help for supported HUD colors. More will be added in the future.\n"
"-If you use screenshots lower than 1680 by 1050px EliteOCR will force you to wait 1,2 seconds on every recognized line.\n"
"-If you changed the FOV settings of the game the limitation may apply on higher resolutions.\n"
"-If the limitations apply the option \"add entries with high confidence\" will be ignored.\"\n"
"-You can remove the limitations if you change to private mode but the export to BPC and EDDN will be disabled.\n"
"-If you have problems with EliteOCR not finding the log files/system names read \"Help\".\n"
"-If you have other problems report them on the Forum (forums.frontier.co.uk) in EliteOCR thread.\n"
"\n"
"-If you are not happy about the limitations: DO NOT USE EliteOCR(nobody is forcing you) and stop complaining.", None))
        self.understood.setText(_translate("Info", "I understood", None))
        self.ok.setText(_translate("Info", "OK", None))

