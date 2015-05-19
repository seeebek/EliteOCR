# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editorUI.ui'
#
# Created: Tue May 19 16:14:02 2015
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

class Ui_Editor(object):
    def setupUi(self, Editor):
        Editor.setObjectName(_fromUtf8("Editor"))
        Editor.resize(728, 577)
        self.verticalLayout = QtGui.QVBoxLayout(Editor)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.table = QtGui.QTableWidget(Editor)
        self.table.setObjectName(_fromUtf8("table"))
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.verticalLayout.addWidget(self.table)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.add_button = QtGui.QPushButton(Editor)
        self.add_button.setObjectName(_fromUtf8("add_button"))
        self.horizontalLayout.addWidget(self.add_button)
        self.delete_button = QtGui.QPushButton(Editor)
        self.delete_button.setObjectName(_fromUtf8("delete_button"))
        self.horizontalLayout.addWidget(self.delete_button)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.save = QtGui.QPushButton(Editor)
        self.save.setObjectName(_fromUtf8("save"))
        self.horizontalLayout.addWidget(self.save)
        self.cancel = QtGui.QPushButton(Editor)
        self.cancel.setObjectName(_fromUtf8("cancel"))
        self.horizontalLayout.addWidget(self.cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Editor)
        QtCore.QObject.connect(self.cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), Editor.close)
        QtCore.QMetaObject.connectSlotsByName(Editor)

    def retranslateUi(self, Editor):
        Editor.setWindowTitle(_translate("Editor", "Commodity Editor", None))
        self.add_button.setText(_translate("Editor", "Add Commodity", None))
        self.delete_button.setText(_translate("Editor", "Delete Row", None))
        self.save.setText(_translate("Editor", "Save", None))
        self.cancel.setText(_translate("Editor", "Cancel", None))

