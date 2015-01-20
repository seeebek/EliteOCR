# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpUI.ui'
#
# Created: Sat Dec 27 11:45:24 2014
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_Help(object):
    def setupUi(self, Help):
        Help.setObjectName(_fromUtf8("Help"))
        Help.resize(630, 478)
        self.verticalLayout = QtGui.QVBoxLayout(Help)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.html_frame = QtWebKit.QWebView(Help)
        self.html_frame.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.html_frame.setObjectName(_fromUtf8("html_frame"))
        self.verticalLayout.addWidget(self.html_frame)

        self.retranslateUi(Help)
        QtCore.QMetaObject.connectSlotsByName(Help)

    def retranslateUi(self, Help):
        Help.setWindowTitle(_translate("Help", "Help", None))

from PyQt4 import QtWebKit
