# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDesktopServices, QDialog
from PyQt4.QtCore import QUrl
from aboutUI import Ui_About

class AboutDialog(QDialog, Ui_About):
    def __init__(self, version):
        QDialog.__init__(self)
        self.setupUi(self)
        self.version.setText("Version " + version)
        self.donate.clicked.connect(self.openDonation)
        
    def openDonation(self):
        QDesktopServices.openUrl(QUrl("http://eliteocr.sourceforge.net/#donate", QUrl.TolerantMode));
        
        
        
