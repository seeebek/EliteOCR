from PyQt4.QtGui import *
from PyQt4.QtCore import QUrl
from helpUI import Ui_Help

class HelpDialog(QDialog, Ui_Help):
    def __init__(self, path):
        QDialog.__init__(self)
        self.setupUi(self)
        helpfile = path+'\\help\\index.html'
        self.html_frame.load(QUrl.fromLocalFile(helpfile))
        