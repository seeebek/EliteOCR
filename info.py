# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QTimer
from infoUI import Ui_Info
from settings import Settings

class InfoDialog(QDialog, Ui_Info):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = Settings()
        self.permit_close = False
        
        self.ok.clicked.connect(self.accepted)
        self.wait = 10
        self.stimer = QTimer
        self.ok.setText(unicode(self.wait))
        self.stimer.singleShot(1000, self.updateTimer)
    
    def updateTimer(self):
        self.wait -= 1
        self.ok.setText(unicode(self.wait))
        if self.wait > 0:
            self.stimer.singleShot(1000, self.updateTimer)
        else:
            self.ok.setEnabled(True)
            self.ok.setText("OK")
    
    def accepted(self):
        if self.understood.isChecked():
            self.permit_close = True
            self.settings.setValue('info_accepted', True)
            self.close()
    
    def closeEvent(self, evnt):
        if self.permit_close:
            super(InfoDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
        