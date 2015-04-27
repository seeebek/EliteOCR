# -*- coding: utf-8 -*-
from PyQt4.QtGui import QTableWidget
from PyQt4.QtCore import Qt

class CustomQTableWidget(QTableWidget):
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self._del_item()
        else:
            QTableWidget.keyPressEvent(self, event)

    def _del_item(self):
        self.removeRow(self.currentRow())
