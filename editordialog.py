from PyQt4.QtGui import QDialog, QTableWidgetItem
from editorUI import Ui_Editor
import json
import codecs

class EditorDialog(QDialog, Ui_Editor):
    def __init__(self, settings):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = settings
        self.save.clicked.connect(self.saveCommodities)
        self.add_button.clicked.connect(self.addCommodity)
        self.delete_button.clicked.connect(self.deleteCommodity)

        file = codecs.open(self.settings.app_path + os.sep + "commodities.json", 'r', "utf-8")
        file_content = file.read()
        commdict = json.loads(file_content)
        file.close()
        titles = []
        for k, v in commdict.iteritems():
            titles = commdict[k].keys()
            break
        titles.remove("rare")
        if str(self.settings["ocr_language"]) in titles:
            titles.remove(str(self.settings["ocr_language"]))
            titles.insert(0,str(self.settings["ocr_language"]))
        
        self.table.setColumnCount(len(titles)+2)
        self.table.setHorizontalHeaderLabels(["rare", "eng"]+titles)
        totable = []
        for k, v in commdict.iteritems():
            rest = [commdict[k][i] for i in titles]
            totable.append([commdict[k]["rare"], k] + rest)
            
        #print totable
        totable.sort(key=lambda x: x[1])
        
        self.table.setRowCount(len(totable))
        for i in xrange(len(totable)):
            for j in xrange(len(totable[i])):
                newitem = QTableWidgetItem(unicode(totable[i][j]))
                #print totable[i][j]
                self.table.setItem(i, j, newitem)
        
    def addCommodity(self):
        self.table.setRowCount(self.table.rowCount()+1)
        
    def deleteCommodity(self):
        self.table.removeRow(self.table.currentRow())
    
    def saveCommodities(self):
        save_dict = {}
        all_rows = self.table.rowCount()
        all_cols = self.table.columnCount()
        
        for row in xrange(all_rows):
            if (not self.table.item(row,0) is None) and (not self.table.item(row,1) is None):
                save_dict[unicode(self.table.item(row,1).text())] = {}
                save_dict[unicode(self.table.item(row,1).text())][unicode(self.table.horizontalHeaderItem(0).text())] = unicode(self.table.item(row,0).text())
                for col in xrange(2,all_cols):
                    if not self.table.item(row,col) is None:
                        save_dict[unicode(self.table.item(row,1).text())][unicode(self.table.horizontalHeaderItem(col).text())] = unicode(self.table.item(row,col).text())
                    else:
                        save_dict[unicode(self.table.item(row,1).text())][unicode(self.table.horizontalHeaderItem(col).text())] = u""
                    #line = self.result_table.item(row,9).text()
        #print save_dict
        
        file = codecs.open(self.settings.app_path + os.sep + "commodities.json", 'w', "utf-8")
        file.write(json.dumps(save_dict, indent=2, separators=(',', ': '), ensure_ascii=False))
        file.close()
        
        self.close()
