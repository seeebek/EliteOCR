# -*- coding: utf-8 -*-
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import QUrl
from helpUI import Ui_Help
import os

class HelpDialog(QDialog, Ui_Help):
    def __init__(self, path):
        QDialog.__init__(self)
        self.setupUi(self)
<<<<<<< HEAD
        helpfile = path + os.sep +"help"+ os.sep +"index.html"
=======
        helpfile = path+os.sep+'help'+os.sep+'index.html'
>>>>>>> master
        self.html_frame.load(QUrl.fromLocalFile(helpfile))
