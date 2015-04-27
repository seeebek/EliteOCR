# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import Qt
from busyUI import Ui_busywidget

class BusyDialog(QDialog, Ui_busywidget):
    def __init__(self, parent):
        QDialog.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowModality(Qt.NonModal)