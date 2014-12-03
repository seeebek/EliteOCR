# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingsUI.ui'
#
# Created: Wed Dec 03 14:25:58 2014
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

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.setEnabled(True)
        Settings.resize(686, 212)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ico/icon.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Settings.setWindowIcon(icon)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Settings)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Settings)
        self.label.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.scr_dir = QtGui.QLineEdit(Settings)
        self.scr_dir.setObjectName(_fromUtf8("scr_dir"))
        self.horizontalLayout.addWidget(self.scr_dir)
        self.browse = QtGui.QPushButton(Settings)
        self.browse.setObjectName(_fromUtf8("browse"))
        self.horizontalLayout.addWidget(self.browse)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtGui.QLabel(Settings)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.exp_dir = QtGui.QLineEdit(Settings)
        self.exp_dir.setObjectName(_fromUtf8("exp_dir"))
        self.horizontalLayout_2.addWidget(self.exp_dir)
        self.exp_browse = QtGui.QPushButton(Settings)
        self.exp_browse.setObjectName(_fromUtf8("exp_browse"))
        self.horizontalLayout_2.addWidget(self.exp_browse)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.auto_fill = QtGui.QCheckBox(Settings)
        self.auto_fill.setObjectName(_fromUtf8("auto_fill"))
        self.verticalLayout.addWidget(self.auto_fill)
        self.remove_dupli = QtGui.QCheckBox(Settings)
        self.remove_dupli.setObjectName(_fromUtf8("remove_dupli"))
        self.verticalLayout.addWidget(self.remove_dupli)
        self.create_nn_images = QtGui.QCheckBox(Settings)
        self.create_nn_images.setChecked(False)
        self.create_nn_images.setObjectName(_fromUtf8("create_nn_images"))
        self.verticalLayout.addWidget(self.create_nn_images)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Settings)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Settings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Settings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(_translate("Settings", "Settings", None))
        self.label.setText(_translate("Settings", "Screenshot Directory:", None))
        self.browse.setText(_translate("Settings", "Browse", None))
        self.label_2.setText(_translate("Settings", "Export Directory:", None))
        self.exp_browse.setText(_translate("Settings", "Browse", None))
        self.auto_fill.setText(_translate("Settings", "Automatically add results with high confidence", None))
        self.remove_dupli.setText(_translate("Settings", "Remove duplicates in Table", None))
        self.create_nn_images.setText(_translate("Settings", "Save digits from processed images to improve OCR accuracy", None))

import res_rc
