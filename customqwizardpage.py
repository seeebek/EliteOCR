# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWizardPage
from PyQt4.QtCore import pyqtSignal

class CustomQWizardPage(QWizardPage):

    pageCreated = pyqtSignal()
    
    def __init__(self):
        QWizardPage.__init__(self)
        self.fullfilled = False
        
    
    def initializePage(self):
        self.show()
        self.pageCreated.emit()
    
    def isComplete (self):
        if self.fullfilled:
            return True
        else:
            return False