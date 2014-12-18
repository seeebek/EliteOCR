from PyQt4.QtGui import QDialog
from editorUI import Ui_Editor
import json

class EditorDialog(QDialog, Ui_Editor):
    def __init__(self, settings):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = settings
        self.save.clicked.connect(self.saveCommodities)
        try:
            file = open(self.settings.app_path + "\\commodities.json", 'r')
            file_content = file.read()
            comm_list = json.loads(file_content)
            file.close()
        except:
            comm_list = ['BEER']
        text = ""
        for line in comm_list:
            text += line+"\n"
        self.commodity_list.setPlainText(text)
        
    def saveCommodities(self):
        commodities = unicode(self.commodity_list.toPlainText()).upper().strip().split("\n")
        commodities = list(set(commodities))
        commodities.sort()
        #print commodities
        commodities = filter(None, commodities)
        file = open(self.settings.app_path + "\\commodities.json", 'w')
        file.write(json.dumps(commodities,indent=2, separators=(',', ': ')))
        file.close()
        self.close()