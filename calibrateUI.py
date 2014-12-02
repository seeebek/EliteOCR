# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calibrateUI.ui'
#
# Created: Wed Nov 26 11:54:01 2014
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

class Ui_Calibrate(object):
    def setupUi(self, Calibrate):
        Calibrate.setObjectName(_fromUtf8("Calibrate"))
        Calibrate.resize(1113, 567)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ico/icon.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Calibrate.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Calibrate)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Calibrate)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.example = QtGui.QGraphicsView(Calibrate)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.example.sizePolicy().hasHeightForWidth())
        self.example.setSizePolicy(sizePolicy)
        self.example.setObjectName(_fromUtf8("example"))
        self.horizontalLayout.addWidget(self.example)
        self.clickarea = QtGui.QGraphicsView(Calibrate)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clickarea.sizePolicy().hasHeightForWidth())
        self.clickarea.setSizePolicy(sizePolicy)
        self.clickarea.setAlignment(QtCore.Qt.AlignCenter)
        self.clickarea.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.clickarea.setObjectName(_fromUtf8("clickarea"))
        self.horizontalLayout.addWidget(self.clickarea)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label_y = QtGui.QLabel(Calibrate)
        self.label_y.setObjectName(_fromUtf8("label_y"))
        self.horizontalLayout_2.addWidget(self.label_y)
        self.prev = QtGui.QPushButton(Calibrate)
        self.prev.setObjectName(_fromUtf8("prev"))
        self.horizontalLayout_2.addWidget(self.prev)
        self.next = QtGui.QPushButton(Calibrate)
        self.next.setObjectName(_fromUtf8("next"))
        self.horizontalLayout_2.addWidget(self.next)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.line = QtGui.QFrame(Calibrate)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.save = QtGui.QPushButton(Calibrate)
        self.save.setObjectName(_fromUtf8("save"))
        self.horizontalLayout_3.addWidget(self.save)
        self.cancel = QtGui.QPushButton(Calibrate)
        self.cancel.setObjectName(_fromUtf8("cancel"))
        self.horizontalLayout_3.addWidget(self.cancel)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Calibrate)
        QtCore.QObject.connect(self.cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), Calibrate.close)
        QtCore.QMetaObject.connectSlotsByName(Calibrate)

    def retranslateUi(self, Calibrate):
        Calibrate.setWindowTitle(_translate("Calibrate", "Calibrate", None))
        self.label.setText(_translate("Calibrate", "Click on the corresponding place in your screenshot to calibrate the OCR areas", None))
        self.label_y.setText(_translate("Calibrate", "y", None))
        self.prev.setText(_translate("Calibrate", "Previous", None))
        self.next.setText(_translate("Calibrate", "Next", None))
        self.save.setText(_translate("Calibrate", "Save", None))
        self.cancel.setText(_translate("Calibrate", "Cancel", None))

import res_rc
