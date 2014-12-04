# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'busyUI.ui'
#
# Created: Wed Dec 03 11:25:03 2014
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

class Ui_busywidget(object):
    def setupUi(self, busywidget):
        busywidget.setObjectName(_fromUtf8("busywidget"))
        busywidget.resize(211, 51)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ico/icon.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        busywidget.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(busywidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(busywidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(busywidget)
        QtCore.QMetaObject.connectSlotsByName(busywidget)

    def retranslateUi(self, busywidget):
        busywidget.setWindowTitle(_translate("busywidget", "OCR in progress", None))
        self.label.setText(_translate("busywidget", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600; color:#750000;\">OCR in progress</span></p></body></html>", None))

import res_rc
